from abc import ABC, abstractmethod
from typing import Any


class CellData(ABC):
    @abstractmethod
    def value(self) -> Any:
        raise NotImplementedError


class BooleanData(CellData):
    def __init__(self, value: bool):
        self._value = value

    def value(self) -> bool:
        return self._value


class IntegerData(CellData):
    def __init__(self, value: int):
        self._value = value

    def value(self) -> int:
        return self._value


class StrData(CellData):
    def __init__(self, value: str):
        self._value = value

    def value(self) -> str:
        return self._value


class BlobData(CellData):
    def __init__(self, value: bytes):
        self._value = value

    def value(self) -> bytes:
        return self._value
