from pathlib import Path

from memdb import DBMS
from memdb.commands.query_factory import QueryFactory
from memdb.config import load_config
from memdb.storage.factory import create_storage
from memdb.setup_logging import log_storage_setup

_COMMANDS = [
    "describe db",
    "create table bitcoins {id int, amount int}",
    "describe db",
    "create table students {id int, name str}",
    "describe db",
    "describe table students",
    "describe table bitcoins",
    "create table departments {id int, dep_name str}",
    "describe db",
    "drop table students",
    "describe db",
    "insert (id, dep_name) into departments (23, SE)",
    "insert (id, dep_name) into departments (23, ab33dd)",
    "select * from departments",
]


def main(config_path: Path | None = None) -> None:
    config = load_config(config_path)
    storage = create_storage(config.storage)
    log_storage_setup(
        config_path=config_path,
        config=config.storage,
        storage=storage,
    )
    dbms = DBMS(storage=storage, query_factory=QueryFactory())
    dbms.init()
    print(f"memdb initialized: {dbms}")
    for index, command in enumerate(_COMMANDS, start=1):
        result = dbms.execute(command)
        print(f"memdb executed-{index}: {result}")
