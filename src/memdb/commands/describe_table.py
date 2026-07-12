from memdb.commands.base import QueryInterface
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData


class DescribeTableQuery(QueryInterface):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def run(self, data: DBData) -> QueryResult:
        table = data.tables.get(self.table_name)
        if table is None:
            return QueryResult(False, f"table {self.table_name} does not exist")

        rows = [[column.name, column.datatype.name()] for column in table.columns]
        return QueryResult(
            True,
            f"Describing table {self.table_name}",
            ["Column", "Type"],
            rows,
        )
