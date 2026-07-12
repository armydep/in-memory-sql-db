from memdb import DBMS
from memdb.commands.query_factory import QueryFactory
from memdb.storage.in_memory_storage import InMemoryStorage


def main() -> None:
    dbms = DBMS(storage=InMemoryStorage(), query_factory=QueryFactory())
    dbms.init()
    print(f"memdb initialized: {dbms}")


if __name__ == "__main__":
    main()
