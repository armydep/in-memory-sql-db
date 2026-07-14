from dataclasses import dataclass, field
from pathlib import Path
import tomllib
from typing import Any

_DEFAULT_SERVER_HOST = "127.0.0.1"
_DEFAULT_SERVER_PORT = 7654


@dataclass(frozen=True)
class StorageConfig:
    enabled: bool = False
    path: Path | None = None
    implementation: str | None = None


@dataclass(frozen=True)
class ServerConfig:
    host: str = _DEFAULT_SERVER_HOST
    port: int = _DEFAULT_SERVER_PORT


@dataclass(frozen=True)
class AppConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


def load_config(path: Path | None = None) -> AppConfig:
    if path is None:
        return AppConfig()

    with path.open("rb") as config_file:
        values = tomllib.load(config_file)

    storage_values = values.get("storage", {})
    if not isinstance(storage_values, dict):
        raise ValueError("[storage] must be a TOML table")
    server_values = values.get("server", {})
    if not isinstance(server_values, dict):
        raise ValueError("[server] must be a TOML table")

    return AppConfig(
        storage=_parse_storage_config(storage_values),
        server=_parse_server_config(server_values),
    )


def _parse_storage_config(values: dict[str, Any]) -> StorageConfig:
    enabled = values.get("enabled", False)
    path = values.get("path")
    implementation = values.get("implementation")

    if type(enabled) is not bool:
        raise ValueError("storage.enabled must be true or false")
    if path is not None and not isinstance(path, str):
        raise ValueError("storage.path must be a string")
    if implementation is not None and not isinstance(implementation, str):
        raise ValueError("storage.implementation must be a string")

    return StorageConfig(
        enabled=enabled,
        path=Path(path) if path is not None else None,
        implementation=implementation,
    )


def _parse_server_config(values: dict[str, Any]) -> ServerConfig:
    host = values.get("host", _DEFAULT_SERVER_HOST)
    port = values.get("port", _DEFAULT_SERVER_PORT)

    if not isinstance(host, str) or not host:
        raise ValueError("server.host must be a non-empty string")
    if type(port) is not int:
        raise ValueError("server.port must be an integer")
    if not 1 <= port <= 65535:
        raise ValueError("server.port must be between 1 and 65535")

    return ServerConfig(host=host, port=port)
