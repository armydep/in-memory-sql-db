from memdb.commands.base import QueryInterface
from memdb.commands.comparison_condition import (
    ComparisonCondition,
    ComparisonOperator,
)
from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class SelectQuery(QueryInterface):
    def __init__(
        self,
        table_name: str,
        condition: ComparisonCondition | None = None,
    ):
        self.table_name = table_name
        self.condition = condition

    def run(self, data: DBData) -> QueryResult:
        table_entry = data.tables.get(self.table_name)
        if table_entry is None:
            return QueryResult(
                success=False,
                message=f"table {self.table_name} does not exist",
            )
        table = table_entry.table

        rows = table.rows
        if self.condition is not None:
            if (
                self.condition.table_name is not None
                and self.condition.table_name != self.table_name
            ):
                return QueryResult(
                    success=False,
                    message=(
                        f"condition refers to table {self.condition.table_name}, "
                        f"but query selects from {self.table_name}"
                    ),
                )

            column_index = next(
                (
                    index
                    for index, column in enumerate(table.columns)
                    if column.name == self.condition.column_name
                ),
                None,
            )
            if column_index is None:
                return QueryResult(
                    success=False,
                    message=(
                        f"column {self.condition.column_name} does not exist "
                        f"in table {self.table_name}"
                    ),
                )

            column = table.columns[column_index]
            if type(self.condition.value) is not column.datatype.python_type():
                return QueryResult(
                    success=False,
                    message=(
                        f"invalid condition value type for column {column.name}: "
                        f"expected {column.datatype.name()}"
                    ),
                )
            if (
                self.condition.operator == ComparisonOperator.GREATER_THAN
                and column.datatype.python_type() is not int
            ):
                return QueryResult(
                    success=False,
                    message=(
                        f"operator > is only supported for INT columns, "
                        f"not {column.datatype.name()}"
                    ),
                )

            index = table_entry.indexes.get(self.condition.column_name)
            if (
                index is not None
                and self.condition.operator == ComparisonOperator.EQUAL
            ):
                rows = index.lookup(self.condition.value)
            else:
                rows = [
                    row
                    for row in rows
                    if self.condition.matches(row.cells[column_index].data.value())
                ]

        return QueryResult(
            success=True,
            message=f"Selected rows from table {self.table_name}",
            columns=[column.name for column in table.columns],
            rows=[
                [cell.data.value() for cell in row.cells]
                for row in rows
            ],
        )
