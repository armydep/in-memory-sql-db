from dataclasses import dataclass
from enum import Enum

from memdb.data.cell_data import CellValue


class ComparisonOperator(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"


@dataclass(frozen=True)
class ComparisonCondition:
    column_name: str
    operator: ComparisonOperator
    value: CellValue
    table_name: str | None = None

    def matches(self, actual_value: CellValue) -> bool:
        if self.operator == ComparisonOperator.EQUAL:
            return actual_value == self.value
        if self.operator == ComparisonOperator.NOT_EQUAL:
            return actual_value != self.value
        if self.operator == ComparisonOperator.GREATER_THAN:
            return actual_value > self.value
        raise ValueError(f"unsupported comparison operator: {self.operator.value}")
