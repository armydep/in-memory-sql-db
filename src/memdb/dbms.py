from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData
from memdb.storage.db_storage import DBStorage


class DBMS:
    def __init__(self, storage: DBStorage, query_factory: QueryFactory) -> None:
        self.storage = storage
        self.query_factory = query_factory
        self.data: DBData | None = None

    def init(self) -> None:
        self.data = self.storage.load()

    def execute(self, command: str) -> QueryResult:
        if self.data is None:
            raise RuntimeError("DBMS has not been initialized")

        query = self.query_factory.create(command)
        result = query.run(self.data)
        if result.success and result.data_changed:
            self.storage.save(self.data)
        return result
