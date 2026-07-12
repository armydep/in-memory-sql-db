from abc import ABC, abstractmethod

from memdb.data.db_data import DBData


class StorageEngine(ABC):
    @abstractmethod
    def load(self) -> DBData:
        raise NotImplementedError

    @abstractmethod
    def save(self, db_data: DBData) -> None:
        raise NotImplementedError
