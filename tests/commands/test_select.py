import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.comparison_condition import (
    ComparisonCondition,
    ComparisonOperator,
)
from memdb.commands.insert import InsertQuery
from memdb.commands.select import SelectQuery
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import BoolType, IntType, StrType


class SelectQueryRunTest(unittest.TestCase):
    def setUp(self):
        self.data = DBData()
        CreateTableQuery(
            "users",
            [
                Column("id", IntType()),
                Column("name", StrType()),
                Column("active", BoolType()),
            ],
        ).run(self.data)

    def test_run_returns_all_columns_and_rows_in_table_order(self):
        InsertQuery(
            "users", {"id": 1, "name": "alice", "active": True}
        ).run(self.data)
        InsertQuery(
            "users", {"id": 2, "name": "bob", "active": False}
        ).run(self.data)

        result = SelectQuery("users").run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Selected rows from table users")
        self.assertEqual(result.columns, ["id", "name", "active"])
        self.assertEqual(result.rows, [[1, "alice", True], [2, "bob", False]])

    def test_run_returns_columns_and_no_rows_for_empty_table(self):
        result = SelectQuery("users").run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.columns, ["id", "name", "active"])
        self.assertEqual(result.rows, [])

    def test_run_filters_rows_with_equal_condition(self):
        InsertQuery(
            "users", {"id": 1, "name": "alice", "active": True}
        ).run(self.data)
        InsertQuery(
            "users", {"id": 2, "name": "bob", "active": False}
        ).run(self.data)
        condition = ComparisonCondition(
            "name", ComparisonOperator.EQUAL, "alice"
        )

        result = SelectQuery("users", condition).run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.rows, [[1, "alice", True]])

    def test_run_filters_rows_with_not_equal_condition(self):
        InsertQuery(
            "users", {"id": 1, "name": "alice", "active": True}
        ).run(self.data)
        InsertQuery(
            "users", {"id": 2, "name": "bob", "active": False}
        ).run(self.data)
        condition = ComparisonCondition(
            "active", ComparisonOperator.NOT_EQUAL, True
        )

        result = SelectQuery("users", condition).run(self.data)

        self.assertEqual(result.rows, [[2, "bob", False]])

    def test_run_filters_rows_with_greater_than_condition(self):
        InsertQuery(
            "users", {"id": 1, "name": "alice", "active": True}
        ).run(self.data)
        InsertQuery(
            "users", {"id": 2, "name": "bob", "active": False}
        ).run(self.data)
        condition = ComparisonCondition("id", ComparisonOperator.GREATER_THAN, 1)

        result = SelectQuery("users", condition).run(self.data)

        self.assertEqual(result.rows, [[2, "bob", False]])

    def test_run_returns_no_rows_when_condition_does_not_match(self):
        condition = ComparisonCondition("id", ComparisonOperator.EQUAL, 99)

        result = SelectQuery("users", condition).run(self.data)

        self.assertTrue(result.success)
        self.assertEqual(result.columns, ["id", "name", "active"])
        self.assertEqual(result.rows, [])

    def test_run_rejects_missing_condition_column(self):
        condition = ComparisonCondition("missing", ComparisonOperator.EQUAL, 1)

        result = SelectQuery("users", condition).run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message, "column missing does not exist in table users"
        )

    def test_run_rejects_wrong_table_qualifier(self):
        condition = ComparisonCondition(
            "id", ComparisonOperator.EQUAL, 1, table_name="orders"
        )

        result = SelectQuery("users", condition).run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "condition refers to table orders, but query selects from users",
        )

    def test_run_rejects_condition_value_with_wrong_type(self):
        condition = ComparisonCondition("id", ComparisonOperator.EQUAL, "1")

        result = SelectQuery("users", condition).run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "invalid condition value type for column id: expected INT",
        )

    def test_run_rejects_greater_than_for_non_integer_column(self):
        condition = ComparisonCondition(
            "name", ComparisonOperator.GREATER_THAN, "alice"
        )

        result = SelectQuery("users", condition).run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "operator > is only supported for INT columns, not STR",
        )

    def test_run_rejects_table_that_does_not_exist(self):
        result = SelectQuery("missing").run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "table missing does not exist")
        self.assertEqual(result.columns, [])
        self.assertEqual(result.rows, [])


if __name__ == "__main__":
    unittest.main()
