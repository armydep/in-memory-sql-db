from memdb.data.cell_metadata import CellMetadata
from memdb.types.datatype import Datatype


class Column:
    def __init__(self, name: str, datatype: Datatype, metadata: CellMetadata | None = None):
        self.name = name
        self.datatype = datatype
        self.metadata = metadata or CellMetadata()
