import unittest
from unittest.mock import Mock

from memdb.commands.create_table import CreateTableQuery
from memdb.commands.delete import DeleteQuery
from memdb.commands.describe_db import DescribeDBQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.query_factory import QueryFactory
from memdb.commands.select import SelectQuery
from memdb.commands.update import UpdateQuery
from memdb.parser.query_parser import QueryParser


class QueryFactoryCreateTest(unittest.TestCase):
    def _assert_delegates_to_parser(self, command, query):
        parser = Mock(spec=QueryParser)
        parser.parse.return_value = query
        factory = QueryFactory(parser=parser)

        result = factory.create(command)

        parser.parse.assert_called_once_with(command)
        self.assertIs(result, query)

    def test_describe_db_delegates_to_parser(self):
        self._assert_delegates_to_parser("describe db", DescribeDBQuery())

    def test_create_table_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            "create table users { id INT }",
            CreateTableQuery("users", []),
        )

    def test_drop_table_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            "drop table users", DropTableQuery("users")
        )

    def test_select_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            "select * from users", SelectQuery("users")
        )

    def test_insert_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            'insert (id, name) into users (1, "alice")',
            InsertQuery("users", {"id": 1, "name": "alice"}),
        )

    def test_delete_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            "delete from users where {id = 5}",
            DeleteQuery("users", "id", 5),
        )

    def test_update_delegates_to_parser(self):
        self._assert_delegates_to_parser(
            'update (1, "alice2") in users where {id = 5}',
            UpdateQuery("users", [1, "alice2"], "id", 5),
        )


if __name__ == "__main__":
    unittest.main()
