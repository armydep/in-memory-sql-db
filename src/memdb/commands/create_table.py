from memdb.commands.base import QueryInterface
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class CreateTableQuery(QueryInterface):
    def __init__(self, table_name: str, columns: list[Column]):
        self.table_name = table_name
        self.columns = columns

    def run_query(self, db_data: DBData) -> QueryResult:
        raise NotImplementedError
