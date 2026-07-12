import unittest

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.delete import DeleteQuery
from memdb.commands.describe import DescribeQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.commands.insert import InsertQuery
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

        self.assertIsInstance(query, DescribeQuery)

    def test_create_table_returns_create_table_query(self):
        query = self.parser.parse("create table users { id INT, name STR }")

        self.assertIsInstance(query, CreateTableQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(
            query.columns,
            [Column("id", IntType()), Column("name", StrType())],
        )

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

    def test_insert_returns_insert_query(self):
        query = self.parser.parse('insert (1, "alice") into users')

        self.assertIsInstance(query, InsertQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(query.values, [1, "alice"])

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


if __name__ == "__main__":
    unittest.main()
