from memdb.data.db_data import DBData
from memdb.query_factory import QueryFactory
from memdb.query_result import QueryResult


class DBMS:
    def __init__(self, db_data: DBData | None = None, query_factory: QueryFactory | None = None):
        self.db_data = db_data or DBData()
        self.query_factory = query_factory or QueryFactory()

    def run_query(self, query_str: str) -> QueryResult:
        query = self.query_factory.create_query(query_str)
        return query.run_query(self.db_data)
