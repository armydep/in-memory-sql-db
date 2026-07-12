from typing import Any

from memdb.commands.base import QueryInterface
from memdb.data.cell import Cell
from memdb.data.cell_data import BlobData, BooleanData, IntegerData, StrData
from memdb.data.db_data import DBData
from memdb.data.row import Row
from memdb.commands.query_result import QueryResult


class InsertQuery(QueryInterface):
    def __init__(self, table_name: str, values: dict[str, Any]):
        self.table_name = table_name
        self.values = values

    def run(self, data: DBData) -> QueryResult:
        table = data.tables.get(self.table_name)
        if table is None:
            return QueryResult(success=False, message=f"table {self.table_name} does not exist")

        defined_columns = {column.name for column in table.columns}
        undefined_columns = [
            column_name
            for column_name in self.values
            if column_name not in defined_columns
        ]
        if undefined_columns:
            return QueryResult(
                success=False,
                message=f"column {undefined_columns[0]} does not exist in table {self.table_name}",
            )

        missing_columns = [
            column.name for column in table.columns if column.name not in self.values
        ]
        if missing_columns:
            return QueryResult(
                success=False,
                message=f"column {missing_columns[0]} is missing",
            )

        data_types = {
            bool: BooleanData,
            int: IntegerData,
            str: StrData,
            bytes: BlobData,
        }
        cells = []
        for column in table.columns:
            value = self.values[column.name]
            expected_type = column.datatype.python_type()
            if type(value) is not expected_type:
                return QueryResult(
                    success=False,
                    message=(
                        f"invalid value type for column {column.name}: "
                        f"expected {column.datatype.name()}"
                    ),
                )
            cells.append(Cell(data_types[expected_type](value)))

        table.rows.append(Row(cells))
        return QueryResult(success=True, message="row added successfully")
