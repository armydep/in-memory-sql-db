import unittest
from pathlib import Path
from threading import Event, Thread
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from memdb.commands.base import QueryAccessMode
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData
from memdb.dbms import DBMS
from memdb.storage.db_storage import DBStorage
from memdb.storage.json_file_storage import JsonFileStorage


class DBMSTest(unittest.TestCase):
    def setUp(self):
        self.data = DBData()
        self.storage = Mock(spec=DBStorage)
        self.storage.load.return_value = self.data
        self.query = Mock()
        self.query.access_mode = QueryAccessMode.WRITE
        self.query_factory = Mock()
        self.query_factory.create.return_value = self.query
        self.dbms = DBMS(self.storage, self.query_factory)
        self.dbms.init()

    def test_saves_after_successful_data_change(self):
        self.query.run.return_value = QueryResult(
            success=True,
            data_changed=True,
        )

        self.dbms.execute("a mutating query")

        self.storage.save.assert_called_once()
        saved_data = self.storage.save.call_args.args[0]
        self.assertIsNot(saved_data, self.data)
        self.assertIs(self.dbms.data, saved_data)

    def test_failed_save_does_not_publish_mutated_working_copy(self):
        def mutate(data):
            data.tables["uncommitted"] = Mock()
            return QueryResult(success=True, data_changed=True)

        self.query.run.side_effect = mutate
        self.storage.save.side_effect = OSError("disk full")

        with self.assertRaisesRegex(OSError, "disk full"):
            self.dbms.execute("a mutating query")

        self.assertIs(self.dbms.data, self.data)
        self.assertNotIn("uncommitted", self.dbms.data.tables)

    def test_does_not_save_after_read_only_query(self):
        self.query.access_mode = QueryAccessMode.READ
        self.query.run.return_value = QueryResult(
            success=True,
            data_changed=False,
        )

        self.dbms.execute("a read-only query")

        self.storage.save.assert_not_called()

    def test_does_not_save_after_failed_query(self):
        self.query.run.return_value = QueryResult(
            success=False,
            data_changed=True,
        )

        self.dbms.execute("a failed query")

        self.storage.save.assert_not_called()

    def test_read_only_queries_can_overlap(self):
        first_started = Event()
        release_first = Event()
        second_started = Event()

        first_query = Mock()
        first_query.access_mode = QueryAccessMode.READ
        second_query = Mock()
        second_query.access_mode = QueryAccessMode.READ

        def run_first(data):
            first_started.set()
            self.assertTrue(release_first.wait(timeout=1))
            return QueryResult(success=True)

        def run_second(data):
            second_started.set()
            return QueryResult(success=True)

        first_query.run.side_effect = run_first
        second_query.run.side_effect = run_second
        self.query_factory.create.side_effect = [first_query, second_query]

        first = Thread(target=self.dbms.execute, args=("first",))
        second = Thread(target=self.dbms.execute, args=("second",))
        first.start()
        self.assertTrue(first_started.wait(timeout=1))
        second.start()

        self.assertTrue(second_started.wait(timeout=1))
        release_first.set()
        first.join(timeout=1)
        second.join(timeout=1)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertTrue(second_started.is_set())

    def test_read_only_query_can_run_while_write_query_is_active(self):
        writer_started = Event()
        release_writer = Event()
        reader_started = Event()

        writer_query = Mock()
        writer_query.access_mode = QueryAccessMode.WRITE
        reader_query = Mock()
        reader_query.access_mode = QueryAccessMode.READ

        def run_writer(data):
            writer_started.set()
            self.assertTrue(release_writer.wait(timeout=1))
            return QueryResult(success=True)

        def run_reader(data):
            reader_started.set()
            return QueryResult(success=True)

        writer_query.run.side_effect = run_writer
        reader_query.run.side_effect = run_reader
        self.query_factory.create.side_effect = [writer_query, reader_query]

        writer = Thread(target=self.dbms.execute, args=("writer",))
        reader = Thread(target=self.dbms.execute, args=("reader",))
        writer.start()
        self.assertTrue(writer_started.wait(timeout=1))
        reader.start()

        self.assertTrue(reader_started.wait(timeout=1))
        release_writer.set()
        writer.join(timeout=1)
        reader.join(timeout=1)

        self.assertFalse(writer.is_alive())
        self.assertFalse(reader.is_alive())
        self.assertTrue(reader_started.is_set())

    def test_write_query_can_prepare_copy_while_read_only_query_is_active(self):
        reader_started = Event()
        release_reader = Event()
        writer_started = Event()

        reader_query = Mock()
        reader_query.access_mode = QueryAccessMode.READ
        writer_query = Mock()
        writer_query.access_mode = QueryAccessMode.WRITE

        def run_reader(data):
            reader_started.set()
            self.assertTrue(release_reader.wait(timeout=1))
            return QueryResult(success=True)

        def run_writer(data):
            writer_started.set()
            return QueryResult(success=True)

        reader_query.run.side_effect = run_reader
        writer_query.run.side_effect = run_writer
        self.query_factory.create.side_effect = [reader_query, writer_query]

        reader = Thread(target=self.dbms.execute, args=("reader",))
        writer = Thread(target=self.dbms.execute, args=("writer",))
        reader.start()
        self.assertTrue(reader_started.wait(timeout=1))
        writer.start()

        self.assertTrue(writer_started.wait(timeout=1))
        release_reader.set()
        reader.join(timeout=1)
        writer.join(timeout=1)

        self.assertFalse(reader.is_alive())
        self.assertFalse(writer.is_alive())
        self.assertTrue(writer_started.is_set())

    def test_active_writer_does_not_block_new_read_only_queries(self):
        first_reader_started = Event()
        release_first_reader = Event()
        writer_started = Event()
        release_writer = Event()
        second_reader_started = Event()

        first_reader_query = Mock()
        first_reader_query.access_mode = QueryAccessMode.READ
        writer_query = Mock()
        writer_query.access_mode = QueryAccessMode.WRITE
        second_reader_query = Mock()
        second_reader_query.access_mode = QueryAccessMode.READ

        def run_first_reader(data):
            first_reader_started.set()
            self.assertTrue(release_first_reader.wait(timeout=1))
            return QueryResult(success=True)

        def run_writer(data):
            writer_started.set()
            self.assertTrue(release_writer.wait(timeout=1))
            return QueryResult(success=True)

        def run_second_reader(data):
            second_reader_started.set()
            return QueryResult(success=True)

        first_reader_query.run.side_effect = run_first_reader
        writer_query.run.side_effect = run_writer
        second_reader_query.run.side_effect = run_second_reader
        self.query_factory.create.side_effect = [
            first_reader_query,
            writer_query,
            second_reader_query,
        ]

        first_reader = Thread(target=self.dbms.execute, args=("first reader",))
        writer = Thread(target=self.dbms.execute, args=("writer",))
        second_reader = Thread(target=self.dbms.execute, args=("second reader",))
        first_reader.start()
        self.assertTrue(first_reader_started.wait(timeout=1))
        writer.start()
        second_reader.start()

        self.assertTrue(writer_started.wait(timeout=1))
        self.assertTrue(second_reader_started.wait(timeout=1))
        release_first_reader.set()
        release_writer.set()

        first_reader.join(timeout=1)
        writer.join(timeout=1)
        second_reader.join(timeout=1)

        self.assertFalse(first_reader.is_alive())
        self.assertFalse(writer.is_alive())
        self.assertFalse(second_reader.is_alive())
        self.assertTrue(second_reader_started.is_set())

    def test_write_queries_block_each_other(self):
        first_started = Event()
        release_first = Event()
        second_started = Event()

        first_query = Mock()
        first_query.access_mode = QueryAccessMode.WRITE
        second_query = Mock()
        second_query.access_mode = QueryAccessMode.WRITE

        def run_first(data):
            first_started.set()
            self.assertTrue(release_first.wait(timeout=1))
            return QueryResult(success=True)

        def run_second(data):
            second_started.set()
            return QueryResult(success=True)

        first_query.run.side_effect = run_first
        second_query.run.side_effect = run_second
        self.query_factory.create.side_effect = [first_query, second_query]

        first = Thread(target=self.dbms.execute, args=("first",))
        second = Thread(target=self.dbms.execute, args=("second",))
        first.start()
        self.assertTrue(first_started.wait(timeout=1))
        second.start()

        self.assertFalse(second_started.wait(timeout=0.1))
        release_first.set()
        first.join(timeout=1)
        second.join(timeout=1)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertTrue(second_started.is_set())

    def test_reader_sees_previous_snapshot_while_writer_is_saving(self):
        save_started = Event()
        release_save = Event()
        second_started = Event()
        first_query = Mock()
        second_query = Mock()
        first_query.access_mode = QueryAccessMode.WRITE
        second_query.access_mode = QueryAccessMode.READ
        def run_first(data):
            data.tables["uncommitted"] = Mock()
            return QueryResult(success=True, data_changed=True)

        first_query.run.side_effect = run_first

        def run_second(data):
            self.assertNotIn("uncommitted", data.tables)
            second_started.set()
            return QueryResult(success=True)

        second_query.run.side_effect = run_second
        self.query_factory.create.side_effect = [first_query, second_query]

        def save(data):
            save_started.set()
            self.assertTrue(release_save.wait(timeout=1))

        self.storage.save.side_effect = save
        first = Thread(target=self.dbms.execute, args=("first",))
        second = Thread(target=self.dbms.execute, args=("second",))
        first.start()
        self.assertTrue(save_started.wait(timeout=1))
        second.start()

        self.assertTrue(second_started.wait(timeout=1))
        release_save.set()
        first.join(timeout=1)
        second.join(timeout=1)

        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertTrue(second_started.is_set())

    def test_persisted_data_is_loaded_by_new_dbms_instance(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "memdb.json"
            first = DBMS(JsonFileStorage(path), QueryFactory())
            first.init()
            self.assertTrue(
                first.execute(
                    "create table users {id int, name str, index (name)}"
                ).success
            )
            self.assertTrue(
                first.execute(
                    'insert (id, name) into users (1, "alice")'
                ).success
            )

            restarted = DBMS(JsonFileStorage(path), QueryFactory())
            restarted.init()
            result = restarted.execute(
                'select * from users where name == "alice"'
            )

            self.assertTrue(result.success)
            self.assertEqual(result.rows, [[1, "alice"]])
            table_entry = restarted.data.tables["users"]
            self.assertIs(
                table_entry.indexes["name"].entries["alice"][0],
                table_entry.table.rows[0],
            )


if __name__ == "__main__":
    unittest.main()
