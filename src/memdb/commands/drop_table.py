from memdb.commands.base import QueryAccessMode, QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class DropTableQuery(QueryInterface):
    access_mode = QueryAccessMode.WRITE

    def __init__(self, table_name: str):
        self.table_name = table_name

    def run(self, data: DBData) -> QueryResult:
        if self.table_name not in data.tables:
            return QueryResult(
                success=False,
                message=f"table {self.table_name} does not exist",
            )

        del data.tables[self.table_name]
        return QueryResult(
            success=True,
            message=f"table {self.table_name} dropped",
            data_changed=True,
        )
