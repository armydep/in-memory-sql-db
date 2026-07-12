# Class Diagram

Core classes and relationships, derived from the original design diagram and
updated to match implemented names (`CellMetadata` attached to `Column`;
`StorageEngine` placeholder added for future persistence).

```mermaid
classDiagram
    direction LR

    class DBMS {
        +run_query(query_str) QueryResult
    }
    class QueryFactory {
        +create_query(query_str) QueryInterface
    }
    class QueryParser {
        +parse(query_str)
    }
    class QueryInterface {
        <<abstract>>
        +run_query(db_data) QueryResult
    }
    class CreateTableQuery
    class SelectQuery
    class QueryResult {
        +success: bool
        +message: str
        +columns: list
        +rows: list
    }

    class DBData {
        +tables: dict~str, Table~
    }
    class Table {
        +name: str
        +columns: list~Column~
        +rows: list~Row~
    }
    class Row {
        +cells: list~Cell~
    }
    class Column {
        +name: str
        +datatype: Datatype
        +metadata: CellMetadata
    }
    class CellMetadata {
        +default_value
        +min_size
        +max_size
    }
    class Cell {
        +data: CellData
    }
    class CellData {
        <<abstract>>
        +value()
    }
    class BooleanData
    class IntegerData
    class StrData
    class BlobData

    class Datatype {
        <<abstract>>
        +name() str
        +python_type() type
    }
    class BoolType
    class IntType
    class StrType
    class BlobType

    class StorageEngine {
        <<abstract>>
        +load() DBData
        +save(db_data)
    }

    DBMS --> QueryFactory
    DBMS --> DBData
    DBMS ..> QueryInterface : executes
    DBMS ..> QueryResult : returns
    QueryFactory --> QueryParser
    QueryFactory ..> QueryInterface : creates
    QueryInterface <|-- CreateTableQuery
    QueryInterface <|-- SelectQuery
    QueryInterface ..> QueryResult : produces

    DBData "1" o-- "*" Table
    Table "1" o-- "*" Column
    Table "1" o-- "*" Row
    Row "1" o-- "*" Cell
    Cell --> CellData
    Column --> Datatype
    Column --> CellMetadata

    CellData <|-- BooleanData
    CellData <|-- IntegerData
    CellData <|-- StrData
    CellData <|-- BlobData

    Datatype <|-- BoolType
    Datatype <|-- IntType
    Datatype <|-- StrType
    Datatype <|-- BlobType

    StorageEngine ..> DBData : loads / saves (future)
```
