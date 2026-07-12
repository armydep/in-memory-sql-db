import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import IntType


class CreateTableQueryRunTest(unittest.TestCase):
    def test_run_creates_table(self):
        data = DBData()
        columns = [Column("id", IntType())]
        query = CreateTableQuery("users", columns)

        result = query.run(data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "table users created")
        self.assertIn("users", data.tables)
        self.assertEqual(data.tables["users"].name, "users")
        self.assertEqual(data.tables["users"].columns, columns)

    def test_run_returns_failure_when_table_already_exists(self):
        data = DBData()
        query = CreateTableQuery("users", [])
        query.run(data)

        result = query.run(data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "table already exists")


if __name__ == "__main__":
    unittest.main()
