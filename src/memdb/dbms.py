from memdb.commands.base import QueryAccessMode
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData
from memdb.rw_lock import RWLock
from memdb.storage.db_storage import DBStorage


class DBMS:
    def __init__(self, storage: DBStorage, query_factory: QueryFactory) -> None:
        self.storage = storage
        self.query_factory = query_factory
        self.data: DBData | None = None
        self._lock = RWLock()

    def init(self) -> None:
        with self._lock.write_locked():
            self.data = self.storage.load()

    def execute(self, command: str, session_id: int | None = None) -> QueryResult:
        query = self.query_factory.create(command)
        if query.access_mode == QueryAccessMode.READ:
            with self._lock.read_locked():
                if self.data is None:
                    raise RuntimeError("DBMS has not been initialized")
                return query.run(self.data)

        with self._lock.write_locked():
            if self.data is None:
                raise RuntimeError("DBMS has not been initialized")

            result = query.run(self.data)
            if result.success and result.data_changed:
                self.storage.save(self.data)
            return result
