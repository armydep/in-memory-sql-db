import logging
from pathlib import Path

from memdb.config import StorageConfig
from memdb.storage.db_storage import DBStorage

logger = logging.getLogger(__name__)


def log_storage_setup(
    config_path: Path | None,
    config: StorageConfig,
    storage: DBStorage,
) -> None:
    selected_implementation = (
        f"{type(storage).__module__}.{type(storage).__qualname__}"
    )
    logger.info(
        "storage setup: config=%s enabled=%s mode=%s path=%s "
        "configured_implementation=%s selected_implementation=%s",
        _absolute_path(config_path) if config_path is not None else "<defaults>",
        config.enabled,
        "persistent" if config.enabled else "in-memory",
        _absolute_path(config.path) if config.path is not None else "<none>",
        config.implementation if config.implementation is not None else "<none>",
        selected_implementation,
    )


def _absolute_path(path: Path) -> Path:
    return path.expanduser().resolve()
