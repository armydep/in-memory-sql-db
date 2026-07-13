import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from memdb.data.cell import Cell
from memdb.data.cell_data import BlobData, BooleanData, IntegerData, StrData
from memdb.data.cell_metadata import CellMetadata
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.row import Row
from memdb.data.table import Table
from memdb.data.types.datatype import BlobType, BoolType, IntType, StrType
from memdb.storage.json_file_storage import JsonFileStorage


class JsonFileStorageTest(unittest.TestCase):
    def test_load_returns_empty_database_when_snapshot_does_not_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"

            data = JsonFileStorage(path).load()

            self.assertEqual(data.tables, {})
            self.assertFalse(path.exists())

    def test_save_and_load_round_trip_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "memdb.json"
            storage = JsonFileStorage(path)

            storage.save(self._database_with_all_types())
            loaded = storage.load()

            self.assertTrue(path.exists())
            table = loaded.tables["records"]
            self.assertEqual(table.name, "records")
            self.assertEqual(
                [column.name for column in table.columns],
                ["id", "name", "active", "payload"],
            )
            self.assertEqual(
                [column.datatype.name() for column in table.columns],
                ["INT", "STR", "BOOL", "BLOB"],
            )
            self.assertEqual(table.columns[1].metadata.default_value, "unknown")
            self.assertEqual(table.columns[1].metadata.min_size, 1)
            self.assertEqual(table.columns[1].metadata.max_size, 100)
            self.assertEqual(
                [cell.data.value() for cell in table.rows[0].cells],
                [1, "alice", True, b"\x00\xff"],
            )

            snapshot = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["version"], 1)
            self.assertIn("metadata", snapshot)
            self.assertIn("data", snapshot)

    def test_load_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memdb.json"
            path.write_text("not JSON", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                JsonFileStorage(path).load()

    def test_load_rejects_unknown_snapshot_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memdb.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 99,
                        "metadata": {"tables": []},
                        "data": {"tables": {}},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError, "unsupported snapshot version 99"
            ):
                JsonFileStorage(path).load()

    def test_failed_replace_keeps_existing_snapshot_and_removes_temp_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memdb.json"
            path.write_text("original", encoding="utf-8")
            storage = JsonFileStorage(path)

            with patch(
                "memdb.storage.json_file_storage.os.replace",
                side_effect=OSError("replace failed"),
            ):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    storage.save(DBData())

            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(list(Path(directory).glob(".memdb.json.*.tmp")), [])

    @staticmethod
    def _database_with_all_types() -> DBData:
        columns = [
            Column("id", IntType()),
            Column(
                "name",
                StrType(),
                CellMetadata(default_value="unknown", min_size=1, max_size=100),
            ),
            Column("active", BoolType()),
            Column("payload", BlobType()),
        ]
        table = Table("records", columns)
        table.rows.append(
            Row(
                [
                    Cell(IntegerData(1)),
                    Cell(StrData("alice")),
                    Cell(BooleanData(True)),
                    Cell(BlobData(b"\x00\xff")),
                ]
            )
        )
        data = DBData()
        data.tables[table.name] = table
        return data


if __name__ == "__main__":
    unittest.main()
