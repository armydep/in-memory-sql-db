from memdb.commands.base import QueryInterface
from memdb.parser.query_parser import QueryParser


class QueryFactory:
    def __init__(self, parser: QueryParser | None = None):
        self.parser = parser or QueryParser()

    def create_query(self, query_str: str) -> QueryInterface:
        raise NotImplementedError
