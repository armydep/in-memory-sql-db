from memdb.commands.base import QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class DropTableQuery(QueryInterface):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
