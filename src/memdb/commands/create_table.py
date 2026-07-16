import re

from memdb.commands.base import QueryAccessMode, QueryInterface
from memdb.commands.index_definition import IndexDefinition
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult
from memdb.data.table import Table

_VALID_TABLE_NAME_RE = re.compile(r"^\w+$")


class CreateTableQuery(QueryInterface):
    access_mode = QueryAccessMode.WRITE

    def __init__(
        self,
        table_name: str,
        columns: list[Column],
        indexes: list[IndexDefinition] | None = None,
    ):
        self.table_name = table_name
        self.columns = columns
        self.indexes = indexes or []

    def run(self, data: DBData) -> QueryResult:
        if not _VALID_TABLE_NAME_RE.fullmatch(self.table_name):
            return QueryResult(success=False, message=f"invalid table name: {self.table_name}")

        if self.table_name in data.tables:
            return QueryResult(success=False, message="table already exists")

        column_names = [column.name for column in self.columns]
        if len(column_names) != len(set(column_names)):
            return QueryResult(success=False, message="duplicate column name")

        data.tables[self.table_name] = Table(self.table_name, self.columns)
        return QueryResult(
            success=True,
            message=f"table {self.table_name} created",
            data_changed=True,
        )
