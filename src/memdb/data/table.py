from memdb.data.column import Column
from memdb.data.row import Row


class Table:
    def __init__(self, name: str, columns: list[Column]):
        self.name = name
        self.columns = columns
        self.rows: list[Row] = []
