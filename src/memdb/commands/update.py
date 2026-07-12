from typing import Any

from memdb.commands.base import QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class UpdateQuery(QueryInterface):
    def __init__(self, table_name: str, values: list[Any], column_name: str, value: Any):
        self.table_name = table_name
        self.values = values
        self.column_name = column_name
        self.value = value

    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
