from memdb.data.db_data import DBData
from memdb.storage.db_storage import DBStorage


class InMemoryStorage(DBStorage):
    def load(self) -> DBData:
        return DBData()

    def save(self, db_data: DBData) -> None:
        pass
