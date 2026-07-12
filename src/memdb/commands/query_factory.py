from memdb.commands.base import QueryInterface
from memdb.parser.query_parser import QueryParser


class QueryFactory:
    def __init__(self, parser: QueryParser | None = None):
        self.parser = parser or QueryParser()

    def create(self, command: str) -> QueryInterface:
        raise NotImplementedError
