from dataclasses import dataclass, field

from memdb.data.cell_data import CellValue
from memdb.data.row import Row


@dataclass
class HashIndex:
    column_name: str
    column_position: int
    entries: dict[CellValue, list[Row]] = field(default_factory=dict)

    def add(self, row: Row) -> None:
        value = row.cells[self.column_position].data.value()
        self.entries.setdefault(value, []).append(row)

    def remove(self, row: Row) -> None:
        value = row.cells[self.column_position].data.value()
        matching_rows = self.entries.get(value)
        if matching_rows is None:
            raise ValueError(f"row is missing from index on {self.column_name}")

        for position, indexed_row in enumerate(matching_rows):
            if indexed_row is row:
                matching_rows.pop(position)
                if not matching_rows:
                    del self.entries[value]
                return
        raise ValueError(f"row is missing from index on {self.column_name}")

    def lookup(self, value: CellValue) -> list[Row]:
        return list(self.entries.get(value, []))

    def contains(self, row: Row) -> bool:
        value = row.cells[self.column_position].data.value()
        return any(indexed_row is row for indexed_row in self.entries.get(value, []))

    def rebuild(self, rows: list[Row]) -> None:
        self.entries.clear()
        for row in rows:
            self.add(row)
