from dataclasses import dataclass

from memdb.data.column import Column


@dataclass
class ParsedCreateTable:
    table_name: str
    columns: list[Column]


@dataclass
class ParsedSelect:
    table_name: str
