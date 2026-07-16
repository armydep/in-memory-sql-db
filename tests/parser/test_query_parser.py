import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.comparison_condition import (
    ComparisonCondition,
    ComparisonOperator,
)
from memdb.commands.delete import DeleteQuery
from memdb.commands.describe_db import DescribeDBQuery
from memdb.commands.describe_table import DescribeTableQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.index_definition import IndexDefinition
from memdb.commands.select import SelectQuery
from memdb.commands.update import UpdateQuery
from memdb.data.column import Column
from memdb.data.types.datatype import IntType, StrType
from memdb.parser.query_parser import QueryParser


class QueryParserParseTest(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_describe_returns_describe_query(self):
        query = self.parser.parse("describe db")

        self.assertIsInstance(query, DescribeDBQuery)

    def test_describe_table_returns_describe_query_with_table_name(self):
        query = self.parser.parse("describe table users")

        self.assertIsInstance(query, DescribeTableQuery)
        self.assertEqual(query.table_name, "users")

    def test_create_table_returns_create_table_query(self):
        query = self.parser.parse("create table users { id INT, name STR }")

        self.assertIsInstance(query, CreateTableQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(
            query.columns,
            [Column("id", IntType()), Column("name", StrType())],
        )
        self.assertEqual(query.indexes, [])

    def test_create_table_parses_single_column_index(self):
        query = self.parser.parse(
            "create table users { id INT, email STR, index (email) }"
        )

        self.assertEqual(
            query.columns,
            [Column("id", IntType()), Column("email", StrType())],
        )
        self.assertEqual(query.indexes, [IndexDefinition("email")])

    def test_create_table_parses_multiple_indexes(self):
        query = self.parser.parse(
            "create table users { index(id), id INT, email STR, INDEX ( email ) }"
        )

        self.assertEqual(
            query.indexes,
            [IndexDefinition("id"), IndexDefinition("email")],
        )

    def test_create_table_rejects_index_for_undefined_column(self):
        with self.assertRaisesRegex(ValueError, "undefined column: email"):
            self.parser.parse("create table users { id INT, index (email) }")

    def test_create_table_rejects_duplicate_index(self):
        with self.assertRaisesRegex(ValueError, "Duplicate index"):
            self.parser.parse(
                "create table users { id INT, index (id), index (id) }"
            )

    def test_create_table_rejects_malformed_index(self):
        with self.assertRaisesRegex(ValueError, "Invalid index definition"):
            self.parser.parse("create table users { id INT, index id }")

    def test_parse_is_case_insensitive(self):
        query = self.parser.parse("CREATE TABLE users { id int, name str }")

        self.assertIsInstance(query, CreateTableQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(
            query.columns,
            [Column("id", IntType()), Column("name", StrType())],
        )

    def test_drop_returns_drop_table_query(self):
        query = self.parser.parse("drop table users")

        self.assertIsInstance(query, DropTableQuery)
        self.assertEqual(query.table_name, "users")

    def test_select_returns_select_query(self):
        query = self.parser.parse("select * from users")

        self.assertIsInstance(query, SelectQuery)
        self.assertEqual(query.table_name, "users")
        self.assertIsNone(query.condition)

    def test_select_parses_unqualified_where_condition(self):
        query = self.parser.parse("select * from users where id == 5")

        self.assertEqual(
            query.condition,
            ComparisonCondition(
                column_name="id",
                operator=ComparisonOperator.EQUAL,
                value=5,
            ),
        )

    def test_select_parses_qualified_where_condition(self):
        query = self.parser.parse(
            'select * from users where users.name != "alice"'
        )

        self.assertEqual(
            query.condition,
            ComparisonCondition(
                table_name="users",
                column_name="name",
                operator=ComparisonOperator.NOT_EQUAL,
                value="alice",
            ),
        )

    def test_select_parses_greater_than_condition(self):
        query = self.parser.parse("select * from users where id > 10")

        self.assertEqual(query.condition.operator, ComparisonOperator.GREATER_THAN)
        self.assertEqual(query.condition.value, 10)

    def test_select_rejects_unsupported_where_operator(self):
        with self.assertRaisesRegex(ValueError, "Unsupported query"):
            self.parser.parse("select * from users where id >= 5")

    def test_select_rejects_incomplete_where_condition(self):
        with self.assertRaisesRegex(ValueError, "Unsupported query"):
            self.parser.parse("select * from users where id ==")

    def test_insert_returns_insert_query(self):
        query = self.parser.parse('insert (id, name) into users (1, "alice")')

        self.assertIsInstance(query, InsertQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(query.values, {"id": 1, "name": "alice"})

    def test_delete_returns_delete_query(self):
        query = self.parser.parse("delete from users where {id = 5}")

        self.assertIsInstance(query, DeleteQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(query.column_name, "id")
        self.assertEqual(query.value, 5)

    def test_update_returns_update_query(self):
        query = self.parser.parse('update (1, "alice2") in users where {id = 5}')

        self.assertIsInstance(query, UpdateQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(query.values, [1, "alice2"])
        self.assertEqual(query.column_name, "id")
        self.assertEqual(query.value, 5)

    def test_insert_quoted_true_and_false_are_kept_as_strings(self):
        query = self.parser.parse(
            'insert (first, second) into flags ("true", "false")'
        )

        self.assertIsInstance(query, InsertQuery)
        self.assertEqual(query.values, {"first": "true", "second": "false"})

    def test_insert_unquoted_true_and_false_are_booleans(self):
        query = self.parser.parse(
            "insert (first, second) into flags (true, false)"
        )

        self.assertIsInstance(query, InsertQuery)
        self.assertEqual(query.values, {"first": True, "second": False})

    def test_insert_rejects_different_number_of_names_and_values(self):
        with self.assertRaisesRegex(ValueError, "same length"):
            self.parser.parse('insert (id, name) into users (1)')

    def test_insert_rejects_duplicate_column_names(self):
        with self.assertRaisesRegex(ValueError, "duplicate column names"):
            self.parser.parse('insert (id, id) into users (1, 2)')

    def test_insert_rejects_empty_column_name(self):
        with self.assertRaisesRegex(ValueError, "empty name"):
            self.parser.parse('insert (id, , name) into users (1, 2, "alice")')

    def test_create_table_rejects_blob_column_type(self):
        with self.assertRaisesRegex(ValueError, "unsupported column type Blob"):
            self.parser.parse("create table files { data BLOB }")

    def test_parse_raises_for_unsupported_query(self):
        with self.assertRaises(ValueError):
            self.parser.parse("frobnicate users")


if __name__ == "__main__":
    unittest.main()
