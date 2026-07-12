# Flowchart — DBMS Lifecycle and Query Execution

Two zoom levels of the same flow: the high-level DBMS lifecycle, and the
detail of a single `execute(command)` call.

## 1. DBMS lifecycle (high level)

```mermaid
flowchart TD
    A["Construct DBMS(storage: DBStorage, query_factory: QueryFactory)"] --> B["data = None"]
    B --> C["init()"]
    C --> D["data = storage.load()"]
    D --> E{"DBMS ready"}
    E -->|"client call"| F["execute(command)"]
    F --> G["QueryResult returned to client"]
    G --> E
    E -.->|"shutdown (future)"| H["storage.save(data)"]
    H -.-> I(["end"])
```

The dashed shutdown path is not implemented in this phase — it marks where
persistence will attach later without changing the rest of the flow.

## 2. execute(command) detail

```mermaid
flowchart TD
    A["execute(command)"] --> B{"data is None?"}
    B -->|"yes"| C["raise RuntimeError: DBMS has not been initialized"]
    B -->|"no"| D["query = query_factory.create(command)"]
    D --> E{"command parses to a known statement?"}
    E -->|"no"| F["parse / factory error"]
    E -->|"yes"| G["query.run(data)"]
    G --> H{"statement executes cleanly?"}
    H -->|"no (e.g. unknown table, type mismatch)"| I["QueryResult(success=False, message=...)"]
    H -->|"yes"| J["QueryResult(success=True, columns/rows or status)"]
    I --> K["return QueryResult"]
    J --> K
```

Open design point (to settle when implementing the parser/factory): whether
a parse/factory error (the `parse / factory error` node) raises an exception
to the caller or is converted into `QueryResult(success=False, ...)` like
statement-level errors. Statement-level errors are already decided:
they return a failed `QueryResult`, they do not raise.
