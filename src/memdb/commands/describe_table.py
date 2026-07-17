from memdb.commands.base import QueryInterface
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData


class DescribeTableQuery(QueryInterface):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def run(self, data: DBData) -> QueryResult:
        table_entry = data.tables.get(self.table_name)
        if table_entry is None:
            return QueryResult(success=False, message=f"table {self.table_name} does not exist")
        table = table_entry.table

        rows = [[column.name, column.datatype.name()] for column in table.columns]
        return QueryResult(
            success=True,
            message=f"Describing table {self.table_name}",
            columns=["Column", "Type"],
            rows=rows,
        )
