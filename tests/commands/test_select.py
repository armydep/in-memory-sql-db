import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.select import SelectQuery
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import IntType, StrType


class SelectQueryRunTest(unittest.TestCase):
    def setUp(self):
        self.data = DBData()
        CreateTableQuery(
            "users",
            [Column("id", IntType()), Column("name", StrType())],
        ).run(self.data)

    def test_run_returns_all_columns_and_rows_in_table_order(self):
        InsertQuery("users", {"id": 1, "name": "alice"}).run(self.data)
        InsertQuery("users", {"id": 2, "name": "bob"}).run(self.data)

        result = SelectQuery("users").run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Selected rows from table users")
        self.assertEqual(result.columns, ["id", "name"])
        self.assertEqual(result.rows, [[1, "alice"], [2, "bob"]])

    def test_run_returns_columns_and_no_rows_for_empty_table(self):
        result = SelectQuery("users").run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.columns, ["id", "name"])
        self.assertEqual(result.rows, [])

    def test_run_rejects_table_that_does_not_exist(self):
        result = SelectQuery("missing").run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "table missing does not exist")
        self.assertEqual(result.columns, [])
        self.assertEqual(result.rows, [])


if __name__ == "__main__":
    unittest.main()
