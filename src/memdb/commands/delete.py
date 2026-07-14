from typing import Any

from memdb.commands.base import QueryAccessMode, QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class DeleteQuery(QueryInterface):
    access_mode = QueryAccessMode.WRITE

    def __init__(self, table_name: str, column_name: str, value: Any):
        self.table_name = table_name
        self.column_name = column_name
        self.value = value

    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
