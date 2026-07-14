import base64
import binascii
import json
from typing import Any

from memdb.commands.query_result import QueryResult


def encode_result(result: QueryResult) -> bytes:
    """Encode a public query response as one UTF-8 JSON line."""
    payload = {
        "success": result.success,
        "message": result.message,
        "columns": result.columns,
        "rows": [
            [_encode_value(value) for value in row]
            for row in result.rows
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def decode_result(line: bytes | str) -> QueryResult:
    """Decode and validate one server response line."""
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    try:
        payload: Any = json.loads(line)
    except json.JSONDecodeError as error:
        raise ValueError("server returned invalid JSON") from error

    if not isinstance(payload, dict):
        raise ValueError("server response must be a JSON object")

    success = payload.get("success")
    message = payload.get("message")
    columns = payload.get("columns")
    rows = payload.get("rows")
    if type(success) is not bool:
        raise ValueError("server response success must be a boolean")
    if message is not None and not isinstance(message, str):
        raise ValueError("server response message must be a string or null")
    if not isinstance(columns, list) or not all(
        isinstance(column, str) for column in columns
    ):
        raise ValueError("server response columns must be a list of strings")
    if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
        raise ValueError("server response rows must be a list of lists")

    return QueryResult(
        success=success,
        message=message,
        columns=columns,
        rows=[[_decode_value(value) for value in row] for row in rows],
    )


def _encode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {
            "$memdb_type": "bytes",
            "base64": base64.b64encode(value).decode("ascii"),
        }
    return value


def _decode_value(value: Any) -> Any:
    if isinstance(value, dict) and value.get("$memdb_type") == "bytes":
        encoded = value.get("base64")
        if not isinstance(encoded, str):
            raise ValueError("server response contains invalid byte data")
        try:
            return base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("server response contains invalid byte data") from error
    return value
