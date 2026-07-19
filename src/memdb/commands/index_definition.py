from dataclasses import dataclass


@dataclass(frozen=True)
class IndexDefinition:
    column_name: str
