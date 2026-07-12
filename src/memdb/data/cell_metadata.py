from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CellMetadata:
    default_value: Optional[Any] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
