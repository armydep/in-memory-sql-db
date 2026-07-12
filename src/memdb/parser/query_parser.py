from memdb.parser.parsed_statement import ParsedCreateTable, ParsedSelect


class QueryParser:
    def parse(self, query_str: str) -> ParsedCreateTable | ParsedSelect:
        raise NotImplementedError
