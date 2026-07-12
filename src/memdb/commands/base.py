from abc import ABC, abstractmethod

from memdb.data.db_data import DBData
from memdb.query_result import QueryResult


class QueryInterface(ABC):
    @abstractmethod
    def run_query(self, db_data: DBData) -> QueryResult:
        raise NotImplementedError
