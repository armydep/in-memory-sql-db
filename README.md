# in-memory-sql-db

An in-memory relational SQL database, available as an embeddable Python
library, local CLI, and a basic multi-user TCP server.

This is a **learning project**, and deliberately so on several fronts at
once: how SQL databases and storage engines work internally, clean
incremental project development, and Python itself — the language, its OOP
model, and the best practices of the Python stack (packaging, testing,
stdlib, and eventually the wider ecosystem).

## Status

Current release: **v1.0.0** — CLI tool with the minimal query set, no
persistence (see `CHANGELOG.md`). This project follows **GitFlow**
(`docs/release-process.md`): `main` holds the released state; `develop`
is the integration branch toward the next version (persistent storage,
per the roadmap below).

`DESCRIBE DB`, `DESCRIBE TABLE`, `CREATE TABLE`, `DROP TABLE`, `SELECT`,
and `INSERT` are implemented end to end (parsed and executed). `DELETE` and
`UPDATE` are parsed but not yet executed (`run()` still raises
`NotImplementedError`).

## Layout

- `src/memdb/` — the `memdb` package: `DBMS` facade, `commands/` (Command
  pattern, one class per SQL statement, plus `QueryFactory`/`QueryResult`),
  `parser/` (hand-written SQL parser), `data/` (in-memory storage: `DBData`,
  `Table`, `Row`, `Column`, `Cell`, and `types/` for column datatypes),
  `storage/` (`DBStorage` persistence interface).
- `tests/` — mirrors `src/memdb/`'s subpackages (`commands/`, `data/`, ...)
  without repeating the `memdb` segment, to avoid a module-name collision
  with the installed package during `unittest discover`. Uses `unittest`.

## Development

```bash
pip install -e .
python -m unittest discover -s tests
```

No runtime dependencies (standard library only).

## CLI

After installing the package, start the interactive SQL prompt with either:

```bash
memdb
# or
python -m memdb
```

Enter one query per line. Use `exit`, `quit`, Ctrl-D, or Ctrl-C to leave the
prompt. The in-memory database is retained until the CLI exits.

The original built-in command sequence remains available as a demo:

```bash
memdb demo
# or
python -m memdb demo
```

## Storage configuration

```bash
memdb --config memdb.toml
memdb demo --config memdb.toml
```

See `memdb.toml.example` for the available settings. With storage disabled,
the CLI uses `InMemoryStorage`. When enabled, `implementation` must be the
fully qualified name of a `DBStorage` subclass and `path` is passed to its
constructor. `JsonFileStorage` stores a versioned JSON snapshot and replaces
it atomically after each successful mutating command.

## TCP server and client

Start the server locally and connect from a second terminal:

```bash
python -m memdb.server --config memdb.toml.example
python -m memdb.client
```

The server owns one shared `DBMS`. Each client connection runs in its own
thread, while a database-wide lock serializes query execution and persistence.
Requests are UTF-8 SQL lines and responses are JSON-encoded query results.

## Docker

Build and start the persistent server:

```bash
docker compose up --build memdb-server
```

Connect from another terminal with `python -m memdb.client`. Create data:

```text
create table users {id int, name str}
insert (id, name) into users (1, "alice")
```

Stop and recreate the container, then reconnect:

```bash
docker compose down
docker compose up memdb-server
```

The following query should return the previously inserted row:

```text
select * from users
```

The `memdb-data` named volume stores `/data/memdb.json` independently of the
container lifecycle. Only `memdb-server` should use that snapshot while the
server is running. The published port is restricted to host loopback by
default. Remove the stored database intentionally with:

```bash
docker compose down --volumes
```

## Roadmap / TODO

1. **Table-level locking** — upgrade the database-wide `RWLock` to per-table
   granularity so writes to different tables can proceed concurrently. Keep a
   whole-database lock (or equivalent) for statements that touch the table
   registry itself (`CREATE TABLE`, `DROP TABLE`).
2. **Transactions** — support `BEGIN`, `COMMIT`, and `ROLLBACK`, with clearly
   defined isolation and failure semantics. Design together with the lock
   granularity above so transaction scope and lock scope stay coherent.
3. **Upgrade the persistence storage engine** — move from one whole-database
   JSON snapshot to a separate file per table (a prerequisite once table-level
   locking lands, so each table's file can be written independently). Fix the
   copy-on-write gap this exposes: `JsonFileStorage.save()` currently walks the
   live `DBData` in place, which is safe today only because a single global
   write lock covers the whole snapshot. Update the `DBStorage` save/load
   contract for per-table granularity, and add BLOB support to the on-disk
   format. Still open beyond this: an object-storage-backed `DBStorage`
   (S3/GCS) for cloud deployment, and backup/recovery tooling beyond today's
   fail-loudly-on-corrupt-snapshot policy.
4. **Multi-user support** — session model and database-wide locking are done
   (thread-per-connection TCP server; writer-preference `RWLock` covering
   query execution and persistence together). Remaining: row-level locking and
   deadlock handling, once table-level locking (above) is in place.
5. **Complete core SQL operations** — implement execution for `UPDATE` and
   `DELETE`, followed by column projections, richer `WHERE` expressions,
   ordering, limits, and joins.
6. **Schema constraints** — add primary keys, uniqueness, nullability, default
   values, and foreign keys with consistent validation and error messages.
7. **Indexes and query planning** — introduce indexes for common lookup paths,
   then add a simple query plan representation and performance benchmarks.
8. **Network API and security** — expose the database through a protocol or
   service API, with authentication, authorization, encrypted connections,
   resource limits, and query timeouts.
9. **Operational tooling** — add structured logging, metrics, health checks,
   import/export commands, and tools for inspecting active sessions and locks.
10. **CLI improvements** — add command history, multiline statements,
    semicolon-delimited input, configurable output formats, and helpful
    commands such as `.help`, `.tables`, and `.quit`.
