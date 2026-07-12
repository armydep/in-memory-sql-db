from memdb.data.cell import Cell


class Row:
    def __init__(self, cells: list[Cell]):
        self.cells = cells
