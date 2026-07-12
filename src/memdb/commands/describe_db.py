from memdb.commands.base import QueryInterface
from memdb.commands.query_result import QueryResult
from memdb.data.db_data import DBData


class DescribeDBQuery(QueryInterface):
    def run(self, data: DBData) -> QueryResult:
        rows = [[table_name] for table_name in data.tables]
        return QueryResult(True, "Describing db", ["Tables"], rows)
