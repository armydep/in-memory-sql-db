import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.data.db_data import DBData


class DropTableQueryRunTest(unittest.TestCase):
    def test_run_drops_existing_table(self):
        data = DBData()
        CreateTableQuery("users", []).run(data)

        result = DropTableQuery("users").run(data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "table users dropped")
        self.assertNotIn("users", data.tables)

    def test_run_returns_failure_when_table_does_not_exist(self):
        result = DropTableQuery("users").run(DBData())

        self.assertFalse(result.success)
        self.assertEqual(result.message, "table users does not exist")


if __name__ == "__main__":
    unittest.main()
