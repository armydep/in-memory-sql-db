import unittest
from unittest.mock import Mock

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.query_factory import QueryFactory
from memdb.commands.select import SelectQuery
from memdb.data.column import Column
from memdb.data.types.datatype import IntType
from memdb.parser.parsed_statement import ParsedCreateTable, ParsedSelect
from memdb.parser.query_parser import QueryParser


class QueryFactoryCreateTest(unittest.TestCase):
    def _factory_with_parsed(self, parsed):
        parser = Mock(spec=QueryParser)
        parser.parse.return_value = parsed
        return QueryFactory(parser=parser), parser

    def test_create_table_statement_returns_create_table_query(self):
        command = "CREATE TABLE users (id INT)"
        columns = [Column("id", IntType())]
        parsed = ParsedCreateTable(table_name="users", columns=columns)
        factory, parser = self._factory_with_parsed(parsed)

        query = factory.create(command)

        parser.parse.assert_called_once_with(command)
        self.assertIsInstance(query, CreateTableQuery)
        self.assertEqual(query.table_name, "users")
        self.assertEqual(query.columns, columns)

    def test_select_statement_returns_select_query(self):
        command = "SELECT * FROM users"
        parsed = ParsedSelect(table_name="users")
        factory, parser = self._factory_with_parsed(parsed)

        query = factory.create(command)

        parser.parse.assert_called_once_with(command)
        self.assertIsInstance(query, SelectQuery)
        self.assertEqual(query.table_name, "users")

    def test_unsupported_parsed_statement_raises_value_error(self):
        parsed = object()
        factory, _ = self._factory_with_parsed(parsed)

        with self.assertRaises(ValueError):
            factory.create("DROP TABLE users")


if __name__ == "__main__":
    unittest.main()
