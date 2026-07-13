import unittest
from unittest.mock import Mock

from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData
from memdb.dbms import DBMS
from memdb.storage.db_storage import DBStorage


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


if __name__ == "__main__":
    unittest.main()
