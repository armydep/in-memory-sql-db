from typing import Any

from memdb.commands.base import QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class InsertQuery(QueryInterface):
    def __init__(self, table_name: str, values: list[Any]):
        self.table_name = table_name
        self.values = values

    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
