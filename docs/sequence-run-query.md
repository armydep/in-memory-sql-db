# Sequence Diagram — Running a Query

Statement lifecycle from client call to returned result, derived from the
original design diagram and updated to match implemented method names.

```mermaid
sequenceDiagram
    actor Client
    participant DBMS
    participant QueryFactory
    participant QueryParser
    participant Query as QueryInterface impl
    participant DBData

    Note over DBMS: init() already called; data is set
    Client->>DBMS: execute(command)
    DBMS->>QueryFactory: create(command)
    QueryFactory->>QueryParser: parse(command)
    QueryParser-->>QueryFactory: parsed statement
    QueryFactory-->>DBMS: QueryInterface instance
    DBMS->>Query: run(data)
    Query->>DBData: read / mutate tables
    DBData-->>Query: data
    Query-->>DBMS: QueryResult
    DBMS-->>Client: QueryResult
```
