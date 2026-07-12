from abc import ABC, abstractmethod

from memdb.data.db_data import DBData
from memdb.commands.query_result import QueryResult


class QueryInterface(ABC):
    @abstractmethod
    def run(self, data: DBData) -> QueryResult:
        raise NotImplementedError
