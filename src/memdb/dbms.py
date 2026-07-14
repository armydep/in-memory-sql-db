from copy import deepcopy
from threading import Lock

from memdb.commands.base import QueryAccessMode
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData
from memdb.storage.db_storage import DBStorage


class DBMS:
    def __init__(self, storage: DBStorage, query_factory: QueryFactory) -> None:
        self.storage = storage
        self.query_factory = query_factory
        self.data: DBData | None = None
        self._writer_lock = Lock()
        self._publication_lock = Lock()

    def init(self) -> None:
        with self._writer_lock:
            loaded_data = self.storage.load()
            with self._publication_lock:
                self.data = loaded_data

    def execute(self, command: str, session_id: int | None = None) -> QueryResult:
        query = self.query_factory.create(command)
        if query.access_mode == QueryAccessMode.READ:
            with self._publication_lock:
                snapshot = self.data
            if snapshot is None:
                raise RuntimeError("DBMS has not been initialized")
            return query.run(snapshot)

        with self._writer_lock:
            with self._publication_lock:
                current_data = self.data
            if current_data is None:
                raise RuntimeError("DBMS has not been initialized")

            working_data = deepcopy(current_data)
            result = query.run(working_data)
            if result.success and result.data_changed:
                self.storage.save(working_data)
                with self._publication_lock:
                    self.data = working_data
            return result
