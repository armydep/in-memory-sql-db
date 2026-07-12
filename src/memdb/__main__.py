from memdb import DBMS
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.storage.in_memory_storage import InMemoryStorage


def main() -> None:
    dbms = DBMS(storage=InMemoryStorage(), query_factory=QueryFactory())
    dbms.init()
    print(f"memdb initialized: {dbms}")
    qr: QueryResult = dbms.execute("describe db")
    print(f"memdb executed-1: {qr}")
    qr = dbms.execute("create table bitcoins {id int, amount int}")
    print(f"memdb executed-2: {qr}")
    qr = dbms.execute("describe db")
    print(f"memdb executed-3: {qr}")
    qr = dbms.execute("create table students {id int, name str}")
    print(f"memdb executed-4: {qr}")
    qr = dbms.execute("describe db")
    print(f"memdb executed-5: {qr}")
    qr = dbms.execute("describe table students")
    print(f"memdb executed-6: {qr}")
    qr = dbms.execute("describe table bitcoins")
    print(f"memdb executed-7: {qr}")

if __name__ == "__main__":
    main()
