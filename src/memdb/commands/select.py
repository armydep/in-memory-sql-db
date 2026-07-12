from memdb.commands.base import QueryInterface
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class SelectQuery(QueryInterface):
    def __init__(self, table_name: str):
        self.table_name = table_name

    def run(self, data: DBData) -> QueryResult:
        table = data.tables.get(self.table_name)
        if table is None:
            return QueryResult(
                success=False,
                message=f"table {self.table_name} does not exist",
            )

        return QueryResult(
            success=True,
            message=f"Selected rows from table {self.table_name}",
            columns=[column.name for column in table.columns],
            rows=[
                [cell.data.value() for cell in row.cells]
                for row in table.rows
            ],
        )
