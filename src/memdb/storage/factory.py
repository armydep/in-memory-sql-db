from importlib import import_module
from typing import cast

from memdb.config import StorageConfig
from memdb.storage.db_storage import DBStorage
from memdb.storage.in_memory_storage import InMemoryStorage


def create_storage(config: StorageConfig) -> DBStorage:
    if not config.enabled:
        return InMemoryStorage()

    if config.path is None:
        raise ValueError("storage.path is required when storage is enabled")
    if config.implementation is None:
        raise ValueError(
            "storage.implementation is required when storage is enabled"
        )

    storage_class = _load_storage_class(config.implementation)
    return storage_class(config.path)


def _load_storage_class(class_path: str) -> type[DBStorage]:
    try:
        module_name, class_name = class_path.rsplit(".", 1)
    except ValueError as error:
        raise ValueError(
            "storage.implementation must be a fully qualified class name"
        ) from error

    try:
        implementation = getattr(import_module(module_name), class_name)
    except (ImportError, AttributeError) as error:
        raise ValueError(
            f"cannot load storage implementation {class_path}"
        ) from error

    if not isinstance(implementation, type) or not issubclass(
        implementation, DBStorage
    ):
        raise TypeError(f"{class_path} does not implement DBStorage")

    return cast(type[DBStorage], implementation)
