import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.describe_db import DescribeDBQuery
from memdb.commands.describe_table import DescribeTableQuery
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import IntType, StrType


class DescribeQueryRunTest(unittest.TestCase):
    def test_describe_db_returns_table_names(self):
        data = DBData()
        CreateTableQuery("users", []).run(data)
        CreateTableQuery("orders", []).run(data)

        result = DescribeDBQuery().run(data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Describing db")
        self.assertEqual(result.columns, ["Tables"])
        self.assertEqual(result.rows, [["users"], ["orders"]])

    def test_describe_table_returns_columns(self):
        data = DBData()
        CreateTableQuery(
            "users",
            [Column("id", IntType()), Column("name", StrType())],
        ).run(data)

        result = DescribeTableQuery("users").run(data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Describing table users")
        self.assertEqual(result.columns, ["Column", "Type"])
        self.assertEqual(result.rows, [["id", "INT"], ["name", "STR"]])

    def test_describe_table_returns_failure_when_table_does_not_exist(self):
        result = DescribeTableQuery("users").run(DBData())

        self.assertFalse(result.success)
        self.assertEqual(result.message, "table users does not exist")


if __name__ == "__main__":
    unittest.main()
