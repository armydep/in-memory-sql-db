import base64
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from memdb.data.cell import Cell
from memdb.data.cell_data import BlobData, BooleanData, IntegerData, StrData
from memdb.data.cell_metadata import CellMetadata
from memdb.data.column import Column
from memdb.data.db_data import DBData
from memdb.data.hash_index import HashIndex
from memdb.data.row import Row
from memdb.data.table import Table
from memdb.data.table_entry import TableEntry
from memdb.data.types.datatype import BlobType, BoolType, IntType, StrType
from memdb.storage.db_storage import DBStorage

_SNAPSHOT_VERSION = 2
_SUPPORTED_SNAPSHOT_VERSIONS = {1, _SNAPSHOT_VERSION}
_DATATYPES = {
    "BLOB": BlobType,
    "BOOL": BoolType,
    "INT": IntType,
    "STR": StrType,
}
_CELL_DATA = {
    "BLOB": BlobData,
    "BOOL": BooleanData,
    "INT": IntegerData,
    "STR": StrData,
}


class JsonFileStorage(DBStorage):
    """Store the complete database as one versioned JSON snapshot."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> DBData:
        try:
            with self.path.open("r", encoding="utf-8") as snapshot_file:
                snapshot = json.load(snapshot_file)
        except FileNotFoundError:
            return DBData()
        except json.JSONDecodeError as error:
            raise ValueError(
                f"cannot load {self.path}: invalid JSON ({error.msg})"
            ) from error

        try:
            return _decode_snapshot(snapshot)
        except ValueError as error:
            raise ValueError(f"cannot load {self.path}: {error}") from error

    def save(self, db_data: DBData) -> None:
        snapshot = _encode_snapshot(db_data)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(snapshot, temporary_file, indent=2, sort_keys=True)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(temporary_path, self.path)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise


def _encode_snapshot(db_data: DBData) -> dict[str, Any]:
    metadata_tables = []
    data_tables = {}

    for table_name, table_entry in db_data.tables.items():
        table = table_entry.table
        if table.name != table_name:
            raise ValueError(
                f"table key {table_name!r} does not match table name {table.name!r}"
            )

        metadata_tables.append(
            {
                "name": table.name,
                "columns": [_encode_column(column) for column in table.columns],
                "indexes": [
                    {"column": index.column_name}
                    for index in table_entry.indexes.values()
                ],
            }
        )
        data_tables[table.name] = [
            _encode_row(row, table.columns) for row in table.rows
        ]

    return {
        "version": _SNAPSHOT_VERSION,
        "metadata": {"tables": metadata_tables},
        "data": {"tables": data_tables},
    }


def _encode_column(column: Column) -> dict[str, Any]:
    datatype = column.datatype.name()
    if datatype not in _DATATYPES:
        raise ValueError(f"unsupported datatype {datatype!r}")

    default_value = column.metadata.default_value
    if (
        default_value is not None
        and type(default_value) is not column.datatype.python_type()
    ):
        raise ValueError(
            f"default value for column {column.name!r} does not match {datatype}"
        )

    min_size = _require_optional_int(
        column.metadata.min_size, f"column {column.name!r} min_size"
    )
    max_size = _require_optional_int(
        column.metadata.max_size, f"column {column.name!r} max_size"
    )

    return {
        "name": column.name,
        "datatype": datatype,
        "cell_metadata": {
            "default_value": _encode_value(default_value),
            "min_size": min_size,
            "max_size": max_size,
        },
    }


def _encode_row(row: Row, columns: list[Column]) -> list[Any]:
    if len(row.cells) != len(columns):
        raise ValueError("row cell count does not match table column count")

    values = []
    for cell, column in zip(row.cells, columns):
        value = cell.data.value()
        if type(value) is not column.datatype.python_type():
            raise ValueError(
                f"cell value for column {column.name!r} does not match "
                f"{column.datatype.name()}"
            )
        values.append(_encode_value(value))
    return values


def _encode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {
            "type": "bytes",
            "base64": base64.b64encode(value).decode("ascii"),
        }
    if value is None or type(value) in {bool, int, str}:
        return value
    raise ValueError(f"unsupported value type {type(value).__name__}")


def _decode_snapshot(snapshot: Any) -> DBData:
    snapshot = _require_dict(snapshot, "snapshot")
    version = snapshot.get("version")
    if type(version) is not int:
        raise ValueError("snapshot version must be an integer")
    if version not in _SUPPORTED_SNAPSHOT_VERSIONS:
        raise ValueError(f"unsupported snapshot version {version}")

    metadata = _require_dict(snapshot.get("metadata"), "metadata")
    metadata_tables = _require_list(metadata.get("tables"), "metadata.tables")
    data = _require_dict(snapshot.get("data"), "data")
    data_tables = _require_dict(data.get("tables"), "data.tables")

    db_data = DBData()
    for table_index, table_value in enumerate(metadata_tables):
        location = f"metadata.tables[{table_index}]"
        table_metadata = _require_dict(table_value, location)
        table_name = _require_string(table_metadata.get("name"), f"{location}.name")
        if table_name in db_data.tables:
            raise ValueError(f"duplicate table name {table_name!r}")

        column_values = _require_list(
            table_metadata.get("columns"), f"{location}.columns"
        )
        columns = [
            _decode_column(column_value, f"{location}.columns[{column_index}]")
            for column_index, column_value in enumerate(column_values)
        ]
        column_names = [column.name for column in columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError(f"duplicate column name in table {table_name!r}")

        indexes = {}
        if version >= 2:
            index_values = _require_list(
                table_metadata.get("indexes"), f"{location}.indexes"
            )
            for index_number, index_value in enumerate(index_values):
                index_location = f"{location}.indexes[{index_number}]"
                index_metadata = _require_dict(index_value, index_location)
                index_column = _require_string(
                    index_metadata.get("column"), f"{index_location}.column"
                )
                if set(index_metadata) != {"column"}:
                    raise ValueError(f"invalid index definition at {index_location}")
                if index_column not in column_names:
                    raise ValueError(
                        f"index references unknown column {index_column!r} "
                        f"at {index_location}"
                    )
                if index_column in indexes:
                    raise ValueError(
                        f"duplicate index for column {index_column!r} at {location}"
                    )
                indexes[index_column] = HashIndex(
                    index_column, column_names.index(index_column)
                )

        if table_name not in data_tables:
            raise ValueError(f"data is missing for table {table_name!r}")
        row_values = _require_list(
            data_tables[table_name], f"data.tables.{table_name}"
        )
        table = Table(table_name, columns)
        table.rows = [
            _decode_row(
                row_value,
                columns,
                f"data.tables.{table_name}[{row_index}]",
            )
            for row_index, row_value in enumerate(row_values)
        ]
        table_entry = TableEntry(table, indexes)
        table_entry.rebuild_indexes()
        db_data.tables[table_name] = table_entry

    if set(data_tables) != set(db_data.tables):
        extra_tables = sorted(set(data_tables) - set(db_data.tables))
        raise ValueError(f"data contains unknown tables: {', '.join(extra_tables)}")

    return db_data


def _decode_column(value: Any, location: str) -> Column:
    column_value = _require_dict(value, location)
    name = _require_string(column_value.get("name"), f"{location}.name")
    datatype_name = _require_string(
        column_value.get("datatype"), f"{location}.datatype"
    )
    datatype_class = _DATATYPES.get(datatype_name)
    if datatype_class is None:
        raise ValueError(f"unsupported datatype {datatype_name!r} at {location}")
    datatype = datatype_class()

    metadata_value = _require_dict(
        column_value.get("cell_metadata"), f"{location}.cell_metadata"
    )
    default_value = _decode_value(
        metadata_value.get("default_value"),
        f"{location}.cell_metadata.default_value",
    )
    if (
        default_value is not None
        and type(default_value) is not datatype.python_type()
    ):
        raise ValueError(f"default value does not match {datatype_name} at {location}")

    metadata = CellMetadata(
        default_value=default_value,
        min_size=_require_optional_int(
            metadata_value.get("min_size"), f"{location}.cell_metadata.min_size"
        ),
        max_size=_require_optional_int(
            metadata_value.get("max_size"), f"{location}.cell_metadata.max_size"
        ),
    )
    return Column(name=name, datatype=datatype, metadata=metadata)


def _decode_row(value: Any, columns: list[Column], location: str) -> Row:
    row_values = _require_list(value, location)
    if len(row_values) != len(columns):
        raise ValueError(f"row cell count does not match column count at {location}")

    cells = []
    for index, (stored_value, column) in enumerate(zip(row_values, columns)):
        cell_location = f"{location}[{index}]"
        decoded_value = _decode_value(stored_value, cell_location)
        if type(decoded_value) is not column.datatype.python_type():
            raise ValueError(
                f"value does not match {column.datatype.name()} at {cell_location}"
            )
        cells.append(Cell(_CELL_DATA[column.datatype.name()](decoded_value)))
    return Row(cells)


def _decode_value(value: Any, location: str) -> Any:
    if isinstance(value, dict):
        if set(value) != {"type", "base64"} or value.get("type") != "bytes":
            raise ValueError(f"invalid encoded value at {location}")
        encoded = _require_string(value.get("base64"), f"{location}.base64")
        try:
            return base64.b64decode(encoded, validate=True)
        except ValueError as error:
            raise ValueError(f"invalid base64 value at {location}") from error
    if value is None or type(value) in {bool, int, str}:
        return value
    raise ValueError(f"unsupported value at {location}")


def _require_dict(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{location} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{location} keys must be strings")
    return value


def _require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{location} must be an array")
    return value


def _require_string(value: Any, location: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{location} must be a string")
    return value


def _require_optional_int(value: Any, location: str) -> int | None:
    if value is not None and type(value) is not int:
        raise ValueError(f"{location} must be an integer or null")
    return value
