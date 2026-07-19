from copy import deepcopy
import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.index_definition import IndexDefinition
from memdb.commands.insert import InsertQuery
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.types.datatype import IntType, StrType


class HashIndexTest(unittest.TestCase):
    def setUp(self):
        self.data = DBData()
        CreateTableQuery(
            "users",
            [Column("id", IntType()), Column("name", StrType())],
            indexes=[IndexDefinition("name")],
        ).run(self.data)
        InsertQuery("users", {"id": 1, "name": "alice"}).run(self.data)

    def test_deepcopy_preserves_shared_row_identity_inside_new_snapshot(self):
        original_entry = self.data.tables["users"]

        copied_data = deepcopy(self.data)
        copied_entry = copied_data.tables["users"]

        self.assertIs(
            copied_entry.table.rows[0],
            copied_entry.indexes["name"].entries["alice"][0],
        )
        self.assertIsNot(copied_entry.table.rows[0], original_entry.table.rows[0])

    def test_remove_row_removes_table_and_index_references(self):
        table_entry = self.data.tables["users"]
        row = table_entry.table.rows[0]

        table_entry.remove_row(row)

        self.assertEqual(table_entry.table.rows, [])
        self.assertEqual(table_entry.indexes["name"].entries, {})


if __name__ == "__main__":
    unittest.main()
