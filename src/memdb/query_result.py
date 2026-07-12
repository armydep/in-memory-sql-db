from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class QueryResult:
    success: bool
    message: Optional[str] = None
    columns: list[str] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)
