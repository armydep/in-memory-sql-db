from abc import ABC, abstractmethod
from enum import Enum, auto

from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class QueryAccessMode(Enum):
    READ = auto()
    WRITE = auto()


class QueryInterface(ABC):
    access_mode = QueryAccessMode.READ

    @abstractmethod
    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
