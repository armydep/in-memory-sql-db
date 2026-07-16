import re
import shlex
from typing import Any

from memdb.commands.base import QueryInterface
from memdb.commands.comparison_condition import (
    ComparisonCondition,
    ComparisonOperator,
)
from memdb.commands.create_table import CreateTableQuery
from memdb.commands.delete import DeleteQuery
from memdb.commands.describe_db import DescribeDBQuery
from memdb.commands.describe_table import DescribeTableQuery
from memdb.commands.drop_table import DropTableQuery
from memdb.commands.insert import InsertQuery
from memdb.commands.index_definition import IndexDefinition
from memdb.commands.select import SelectQuery
from memdb.commands.update import UpdateQuery
from memdb.data.column import Column
from memdb.data.types.datatype import BoolType, Datatype, IntType, StrType


_CREATE_TABLE_RE = re.compile(
    r"^create\s+table\s+(?P<table>\w+)\s*\{\s*(?P<columns>.*?)\s*\}$",
    re.IGNORECASE | re.DOTALL,
)
_INDEX_DEFINITION_RE = re.compile(
    r"^index\s*\(\s*(?P<column>\w+)\s*\)$",
    re.IGNORECASE,
)
_DESCRIBE_TABLE_RE = re.compile(
    r"^describe\s+table\s+(?P<table>\w+)$",
    re.IGNORECASE,
)
_DROP_TABLE_RE = re.compile(r"^drop\s+table\s+(?P<table>\w+)$", re.IGNORECASE)
_SELECT_RE = re.compile(
    r"^select\s+\*\s+from\s+(?P<table>\w+)"
    r"(?:\s+where\s+(?:(?P<condition_table>\w+)\.)?"
    r"(?P<column>\w+)\s*(?P<operator>==(?!=)|!=(?!=)|>(?!=))"
    r"\s*(?P<value>.+))?$",
    re.IGNORECASE,
)
_INSERT_RE = re.compile(
    r"^insert\s*\((?P<rows>.*?)\)\s+into\s+(?P<table>\w+)\s*\((?P<values>.*?)\)$",
    re.IGNORECASE | re.DOTALL,
)
_DELETE_RE = re.compile(
    r"^delete\s+from\s+(?P<table>\w+)\s+where\s*\{\s*(?P<column>\w+)\s*=\s*(?P<value>.*?)\s*\}$",
    re.IGNORECASE | re.DOTALL,
)
_UPDATE_RE = re.compile(
    r"^update\s*\((?P<values>.*?)\)\s+in\s+(?P<table>\w+)\s+where\s*\{\s*(?P<column>\w+)\s*=\s*(?P<value>.*?)\s*\}$",
    re.IGNORECASE | re.DOTALL,
)

_DATA_TYPES: dict[str, type[Datatype]] = {
    "BOOL": BoolType,
    "INT": IntType,
    "STR": StrType,
}


class QueryParser:
    def parse(self, query_str: str) -> QueryInterface:
        """
        Matches the trimmed query string against a fixed-format regex per
        statement keyword (DESCRIBE DB / DESCRIBE TABLE / CREATE TABLE /
        DROP TABLE / SELECT / INSERT / DELETE / UPDATE) and constructs the
        matching QueryInterface implementation from the captured groups.
        Raises ValueError if no statement's grammar matches.
        """
        query = query_str.strip()

        if query.lower() == "describe db":
            return DescribeDBQuery()

        if match := _DESCRIBE_TABLE_RE.fullmatch(query):
            return DescribeTableQuery(match.group("table"))

        if match := _CREATE_TABLE_RE.fullmatch(query):
            columns, indexes = self._parse_table_elements(match.group("columns"))
            return CreateTableQuery(
                match.group("table"),
                columns,
                indexes,
            )

        if match := _DROP_TABLE_RE.fullmatch(query):
            return DropTableQuery(match.group("table"))

        if match := _SELECT_RE.fullmatch(query):
            condition = None
            if column_name := match.group("column"):
                condition = ComparisonCondition(
                    table_name=match.group("condition_table"),
                    column_name=column_name,
                    operator=ComparisonOperator(match.group("operator")),
                    value=self._parse_value(match.group("value")),
                )
            return SelectQuery(match.group("table"), condition)

        if match := _INSERT_RE.fullmatch(query):
            rows_str = match.group("rows").strip()
            row_names = [row.strip() for row in rows_str.split(",")] if rows_str else []
            if any(not name for name in row_names):
                raise ValueError("INSERT column list contains an empty name")

            values = self._parse_values(match.group("values"))
            if len(row_names) != len(values):
                raise ValueError(
                    "INSERT row names and values must have the same length"
                )
            if len(row_names) != len(set(row_names)):
                raise ValueError("INSERT contains duplicate column names")

            return InsertQuery(
                match.group("table"),
                dict(zip(row_names, values)),
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

    def _parse_table_elements(
        self, elements_str: str
    ) -> tuple[list[Column], list[IndexDefinition]]:
        if not elements_str.strip():
            return [], []

        columns = []
        indexes = []
        for element in elements_str.split(","):
            declaration = element.strip()
            if not declaration:
                raise ValueError("Invalid empty table definition")
            if re.match(r"^index\b", declaration, re.IGNORECASE):
                match = _INDEX_DEFINITION_RE.fullmatch(declaration)
                if match is None:
                    raise ValueError(f"Invalid index definition: {declaration}")
                indexes.append(IndexDefinition(match.group("column")))
            else:
                columns.extend(self._parse_columns(declaration))

        column_names = {column.name for column in columns}
        for index in indexes:
            if index.column_name not in column_names:
                raise ValueError(
                    f"Index references undefined column: {index.column_name}"
                )

        indexed_columns = [index.column_name for index in indexes]
        if len(indexed_columns) != len(set(indexed_columns)):
            raise ValueError("Duplicate index definition")

        return columns, indexes

    def _parse_datatype(self, datatype_name: str) -> Datatype:
        if datatype_name.upper() == "BLOB":
            raise ValueError("unsupported column type Blob")

        datatype_class = _DATA_TYPES.get(datatype_name.upper())
        if datatype_class is None:
            raise ValueError(f"Unsupported datatype: {datatype_name}")

        return datatype_class()

    def _parse_values(self, values_str: str) -> list[Any]:
        if not values_str.strip():
            return []

        # posix=False keeps the surrounding quote characters in each token
        # (rather than stripping them), so _parse_value can tell a quoted
        # string like "true" apart from the bareword true.
        lexer = shlex.shlex(values_str, posix=False)
        lexer.whitespace = ","
        lexer.whitespace_split = True
        return [self._parse_value(value) for value in lexer]

    def _parse_value(self, value_str: str) -> Any:
        value = value_str.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            return value[1:-1]

        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False
        if value.isdecimal() or (value.startswith("-") and value[1:].isdecimal()):
            return int(value)

        return value
