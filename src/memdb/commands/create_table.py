import re

from memdb.commands.base import QueryAccessMode, QueryInterface
from memdb.commands.index_definition import IndexDefinition
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.hash_index import HashIndex
from memdb.commands.query_result import QueryResult
from memdb.data.table import Table
from memdb.data.table_entry import TableEntry

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

        index_names = [index.column_name for index in self.indexes]
        if len(index_names) != len(set(index_names)):
            return QueryResult(success=False, message="duplicate index definition")
        undefined_indexes = [
            index_name for index_name in index_names if index_name not in column_names
        ]
        if undefined_indexes:
            return QueryResult(
                success=False,
                message=f"index references undefined column: {undefined_indexes[0]}",
            )

        table = Table(self.table_name, self.columns)
        indexes = {
            index_name: HashIndex(index_name, column_names.index(index_name))
            for index_name in index_names
        }
        data.tables[self.table_name] = TableEntry(table, indexes)
        return QueryResult(
            success=True,
            message=f"table {self.table_name} created",
            data_changed=True,
        )
