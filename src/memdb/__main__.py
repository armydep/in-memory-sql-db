from memdb import DBMS
from memdb.commands.query_factory import QueryFactory
from memdb.storage.in_memory_storage import InMemoryStorage

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


def main() -> None:
    dbms = DBMS(storage=InMemoryStorage(), query_factory=QueryFactory())
    dbms.init()
    print(f"memdb initialized: {dbms}")
    for i, command in enumerate(_COMMANDS, start=1):
        result = dbms.execute(command)
        print(f"memdb executed-{i}: {result}")


if __name__ == "__main__":
    main()
