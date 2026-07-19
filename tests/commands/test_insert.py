import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.index_definition import IndexDefinition
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import IntType, StrType


class InsertQueryRunTest(unittest.TestCase):
    def setUp(self):
        self.data = DBData()
        CreateTableQuery(
            "users",
            [Column("id", IntType()), Column("name", StrType())],
            indexes=[IndexDefinition("id"), IndexDefinition("name")],
        ).run(self.data)

    def test_run_rejects_column_that_is_not_defined_in_table(self):
        query = InsertQuery("users", {"id": 1, "email": "a@example.com"})

        result = query.run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "column email does not exist in table users",
        )

    def test_run_adds_row_in_table_column_order(self):
        query = InsertQuery("users", {"name": "alice", "id": 1})

        result = query.run(self.data)

        self.assertTrue(result.success)
        self.assertTrue(result.data_changed)
        self.assertEqual(result.message, "row added successfully")
        self.assertEqual(len(self.data.tables["users"].table.rows), 1)
        self.assertEqual(
            [
                cell.data.value()
                for cell in self.data.tables["users"].table.rows[0].cells
            ],
            [1, "alice"],
        )
        row = self.data.tables["users"].table.rows[0]
        self.assertIs(self.data.tables["users"].indexes["id"].entries[1][0], row)
        self.assertIs(
            self.data.tables["users"].indexes["name"].entries["alice"][0],
            row,
        )

    def test_run_groups_duplicate_index_values_as_row_references(self):
        InsertQuery("users", {"id": 1, "name": "alice"}).run(self.data)
        InsertQuery("users", {"id": 2, "name": "alice"}).run(self.data)

        table_entry = self.data.tables["users"]
        matching_rows = table_entry.indexes["name"].entries["alice"]

        self.assertEqual(len(matching_rows), 2)
        self.assertIs(matching_rows[0], table_entry.table.rows[0])
        self.assertIs(matching_rows[1], table_entry.table.rows[1])

    def test_run_rejects_missing_column(self):
        result = InsertQuery("users", {"id": 1}).run(self.data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "column name is missing")

    def test_run_rejects_value_with_wrong_type(self):
        result = InsertQuery("users", {"id": "one", "name": "alice"}).run(
            self.data
        )

        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "invalid value type for column id: expected INT",
        )


if __name__ == "__main__":
    unittest.main()
