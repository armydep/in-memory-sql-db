from memdb.commands.base import QueryInterface
from memdb.data.db_data import DBData
from memdb.query_result import QueryResult


class SelectQuery(QueryInterface):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def run_query(self, db_data: DBData) -> QueryResult:
        raise NotImplementedError
