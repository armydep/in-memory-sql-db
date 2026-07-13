from dataclasses import dataclass, field
from pathlib import Path
import tomllib
from typing import Any


@dataclass(frozen=True)
class StorageConfig:
    enabled: bool = False
    path: Path | None = None
    implementation: str | None = None


@dataclass(frozen=True)
class AppConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)


def load_config(path: Path | None = None) -> AppConfig:
    if path is None:
        return AppConfig()

    with path.open("rb") as config_file:
        values = tomllib.load(config_file)

    storage_values = values.get("storage", {})
    if not isinstance(storage_values, dict):
        raise ValueError("[storage] must be a TOML table")

    return AppConfig(storage=_parse_storage_config(storage_values))


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
