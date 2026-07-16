import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.index_definition import IndexDefinition
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
        self.assertTrue(result.data_changed)
        self.assertEqual(result.message, "table users created")
        self.assertIn("users", data.tables)
        self.assertEqual(data.tables["users"].name, "users")
        self.assertEqual(data.tables["users"].columns, columns)

    def test_run_accepts_parsed_index_state_without_creating_index(self):
        data = DBData()
        columns = [Column("id", IntType())]
        query = CreateTableQuery(
            "users", columns, indexes=[IndexDefinition("id")]
        )

        result = query.run(data)

        self.assertTrue(result.success)
        self.assertEqual(query.indexes, [IndexDefinition("id")])
        self.assertFalse(hasattr(data.tables["users"], "indexes"))

    def test_run_returns_failure_when_table_already_exists(self):
        data = DBData()
        query = CreateTableQuery("users", [])
        query.run(data)

        result = query.run(data)

        self.assertFalse(result.success)
        self.assertFalse(result.data_changed)
        self.assertEqual(result.message, "table already exists")

    def test_run_accepts_table_name_with_digits_and_underscores(self):
        data = DBData()
        query = CreateTableQuery("table_1", [])

        result = query.run(data)

        self.assertTrue(result.success)
        self.assertIn("table_1", data.tables)

    def test_run_returns_failure_for_invalid_table_name(self):
        data = DBData()
        query = CreateTableQuery("bad name", [])

        result = query.run(data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "invalid table name: bad name")
        self.assertNotIn("bad name", data.tables)

    def test_run_returns_failure_for_duplicate_column_names(self):
        data = DBData()
        columns = [Column("id", IntType()), Column("id", IntType())]
        query = CreateTableQuery("users", columns)

        result = query.run(data)

        self.assertFalse(result.success)
        self.assertEqual(result.message, "duplicate column name")
        self.assertNotIn("users", data.tables)


if __name__ == "__main__":
    unittest.main()
