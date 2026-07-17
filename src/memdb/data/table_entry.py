from dataclasses import dataclass, field

from memdb.data.hash_index import HashIndex
from memdb.data.row import Row
from memdb.data.table import Table


@dataclass
class TableEntry:
    table: Table
    indexes: dict[str, HashIndex] = field(default_factory=dict)

    def add_row(self, row: Row) -> None:
        self.table.rows.append(row)
        added_indexes = []
        try:
            for index in self.indexes.values():
                index.add(row)
                added_indexes.append(index)
        except Exception:
            for index in reversed(added_indexes):
                index.remove(row)
            self.table.rows.pop()
            raise

    def remove_row(self, row: Row) -> None:
        table_position = next(
            (
                position
                for position, table_row in enumerate(self.table.rows)
                if table_row is row
            ),
            None,
        )
        if table_position is None:
            raise ValueError("row is missing from table")
        missing_indexes = [
            index.column_name
            for index in self.indexes.values()
            if not index.contains(row)
        ]
        if missing_indexes:
            raise ValueError(f"row is missing from index on {missing_indexes[0]}")

        for index in self.indexes.values():
            index.remove(row)
        self.table.rows.pop(table_position)

    def rebuild_indexes(self) -> None:
        for index in self.indexes.values():
            index.rebuild(self.table.rows)
