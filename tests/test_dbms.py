import unittest
from pathlib import Path
from threading import Event, Thread
from tempfile import TemporaryDirectory
from unittest.mock import Mock

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

        self.storage.save.assert_called_once_with(self.data)

    def test_does_not_save_after_read_only_query(self):
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

    def test_serializes_query_execution(self):
        first_started = Event()
        release_first = Event()
        second_started = Event()

        first_query = Mock()
        second_query = Mock()

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

    def test_save_is_part_of_serialized_execution(self):
        save_started = Event()
        release_save = Event()
        second_started = Event()
        first_query = Mock()
        second_query = Mock()
        first_query.run.return_value = QueryResult(success=True, data_changed=True)

        def run_second(data):
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

        self.assertFalse(second_started.wait(timeout=0.1))
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
                first.execute("create table users {id int, name str}").success
            )
            self.assertTrue(
                first.execute(
                    'insert (id, name) into users (1, "alice")'
                ).success
            )

            restarted = DBMS(JsonFileStorage(path), QueryFactory())
            restarted.init()
            result = restarted.execute("select * from users")

            self.assertTrue(result.success)
            self.assertEqual(result.rows, [[1, "alice"]])


if __name__ == "__main__":
    unittest.main()
