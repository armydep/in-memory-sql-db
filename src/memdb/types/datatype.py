from abc import ABC, abstractmethod


class Datatype(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def python_type(self) -> type:
        raise NotImplementedError


class BoolType(Datatype):
    def name(self) -> str:
        return "BOOL"

    def python_type(self) -> type:
        return bool


class IntType(Datatype):
    def name(self) -> str:
        return "INT"

    def python_type(self) -> type:
        return int


class StrType(Datatype):
    def name(self) -> str:
        return "STR"

    def python_type(self) -> type:
        return str


class BlobType(Datatype):
    def name(self) -> str:
        return "BLOB"

    def python_type(self) -> type:
        return bytes
