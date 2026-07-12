from memdb.commands.base import QueryInterface
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult
from memdb.data.table import Table


class CreateTableQuery(QueryInterface):
    def __init__(self, table_name: str, columns: list[Column]):
        self.table_name = table_name
        self.columns = columns

    def run(self, data: DBData) -> QueryResult:
        if not self.table_name or not self.table_name.isalpha():
            raise ValueError(f"Invalid table name: {self.table_name}")

        if self.table_name in data.tables:
            return QueryResult(False, "table already exists")

        data.tables[self.table_name] = Table(self.table_name, self.columns)
        return QueryResult(True, f"table {self.table_name} created")
