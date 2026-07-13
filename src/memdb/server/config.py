from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 7654


@dataclass(frozen=True)
class ServerConfig:
    host: str = _DEFAULT_HOST
    port: int = _DEFAULT_PORT


def load_server_config(path: Path | None = None) -> ServerConfig:
    if path is None:
        return ServerConfig()

    with path.open("rb") as config_file:
        values = tomllib.load(config_file)

    server_values = values.get("server", {})
    if not isinstance(server_values, dict):
        raise ValueError("[server] must be a TOML table")

    return _parse_server_config(server_values)


def _parse_server_config(values: dict[str, Any]) -> ServerConfig:
    host = values.get("host", _DEFAULT_HOST)
    port = values.get("port", _DEFAULT_PORT)

    if not isinstance(host, str) or not host:
        raise ValueError("server.host must be a non-empty string")
    if type(port) is not int:
        raise ValueError("server.port must be an integer")
    if not 1 <= port <= 65535:
        raise ValueError("server.port must be between 1 and 65535")

    return ServerConfig(host=host, port=port)
