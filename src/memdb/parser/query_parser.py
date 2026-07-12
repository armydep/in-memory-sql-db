import re
import shlex
from typing import Any

from memdb.commands.base import QueryInterface
from memdb.commands.create_table import CreateTableQuery
from memdb.commands.delete import DeleteQuery
from memdb.commands.describe import DescribeQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.select import SelectQuery
from memdb.commands.update import UpdateQuery
from memdb.data.column import Column
from memdb.data.types.datatype import BlobType, BoolType, Datatype, IntType, StrType


_CREATE_TABLE_RE = re.compile(
    r"^create\s+table\s+(?P<table>\w+)\s*\{\s*(?P<columns>.*?)\s*\}$",
    re.IGNORECASE,
)
_DROP_TABLE_RE = re.compile(r"^drop\s+table\s+(?P<table>\w+)$", re.IGNORECASE)
_SELECT_RE = re.compile(r"^select\s+\*\s+from\s+(?P<table>\w+)$", re.IGNORECASE)
_INSERT_RE = re.compile(
    r"^insert\s*\((?P<values>.*?)\)\s+into\s+(?P<table>\w+)$",
    re.IGNORECASE,
)
_DELETE_RE = re.compile(
    r"^delete\s+from\s+(?P<table>\w+)\s+where\s*\{\s*(?P<column>\w+)\s*=\s*(?P<value>.*?)\s*\}$",
    re.IGNORECASE,
)
_UPDATE_RE = re.compile(
    r"^update\s*\((?P<values>.*?)\)\s+in\s+(?P<table>\w+)\s+where\s*\{\s*(?P<column>\w+)\s*=\s*(?P<value>.*?)\s*\}$",
    re.IGNORECASE,
)

_DATA_TYPES: dict[str, type[Datatype]] = {
    "BOOL": BoolType,
    "INT": IntType,
    "STR": StrType,
    "BLOB": BlobType,
}


class QueryParser:
    def parse(self, query_str: str) -> QueryInterface:
        """
        1. split query str into list of tokens (with trimming head and tail each one)
        2. switch case on first token:
         case SELECT:
           RETURN select_query
         case CREATE:
           RETURN create_table_query
         case UPDATE:
           RETURN update_query
         case INSERT:
           RETURN insert_query
         case DELETE:
           RETURN delete_query
         case DROP:
           RETURN drop_table_query
         case DESCRIBE:
           RETURN describe_table_query
        :param query_str:
        :return:
        """
        query = query_str.strip()

        if query.lower() == "describe db":
            return DescribeQuery()

        if match := _CREATE_TABLE_RE.fullmatch(query):
            return CreateTableQuery(
                match.group("table"),
                self._parse_columns(match.group("columns")),
            )

        if match := _DROP_TABLE_RE.fullmatch(query):
            return DropTableQuery(match.group("table"))

        if match := _SELECT_RE.fullmatch(query):
            return SelectQuery(match.group("table"))

        if match := _INSERT_RE.fullmatch(query):
            return InsertQuery(
                match.group("table"),
                self._parse_values(match.group("values")),
            )

        if match := _DELETE_RE.fullmatch(query):
            return DeleteQuery(
                match.group("table"),
                match.group("column"),
                self._parse_value(match.group("value")),
            )

        if match := _UPDATE_RE.fullmatch(query):
            return UpdateQuery(
                match.group("table"),
                self._parse_values(match.group("values")),
                match.group("column"),
                self._parse_value(match.group("value")),
            )

        raise ValueError(f"Unsupported query: {query_str}")

    def _parse_columns(self, columns_str: str) -> list[Column]:
        if not columns_str.strip():
            return []

        columns = []
        for column_str in columns_str.split(","):
            parts = column_str.strip().split()
            if len(parts) != 2:
                raise ValueError(f"Invalid column definition: {column_str}")

            column_name, datatype_name = parts
            datatype = self._parse_datatype(datatype_name)
            columns.append(Column(column_name, datatype))

        return columns

    def _parse_datatype(self, datatype_name: str) -> Datatype:
        datatype_class = _DATA_TYPES.get(datatype_name.upper())
        if datatype_class is None:
            raise ValueError(f"Unsupported datatype: {datatype_name}")

        return datatype_class()

    def _parse_values(self, values_str: str) -> list[Any]:
        if not values_str.strip():
            return []

        lexer = shlex.shlex(values_str, posix=True)
        lexer.whitespace = ","
        lexer.whitespace_split = True
        return [self._parse_value(value) for value in lexer]

    def _parse_value(self, value_str: str) -> Any:
        value = value_str.strip()
        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False
        if value.isdecimal() or (value.startswith("-") and value[1:].isdecimal()):
            return int(value)

        return value
