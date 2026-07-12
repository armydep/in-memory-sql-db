from dataclasses import dataclass, field

from memdb.data.cell_metadata import CellMetadata
from memdb.data.types.datatype import Datatype


@dataclass
class Column:
    name: str
    datatype: Datatype
    metadata: CellMetadata = field(default_factory=CellMetadata)
