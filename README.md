# in-memory-sql-db

An in-memory relational SQL database, built as an embeddable Python library
(no network server in this phase).

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

## Roadmap / TODO

1. **Persistent storage** — implement additional `DBStorage` backends and
   evaluate cloud deployment options such as object storage and persistent
   volumes. Define a versioned on-disk format, atomic writes, backups, and
   recovery behavior.
2. **Multi-user support** — add a server-facing session model and a locking
   mechanism for safe concurrent access. Start with database- or table-level
   locks, then consider row-level locks and deadlock handling as needed.
3. **Complete core SQL operations** — implement execution for `UPDATE` and
   `DELETE`, followed by column projections, richer `WHERE` expressions,
   ordering, limits, and joins.
4. **Transactions** — support `BEGIN`, `COMMIT`, and `ROLLBACK`, with clearly
   defined isolation and failure semantics.
5. **Schema constraints** — add primary keys, uniqueness, nullability, default
   values, and foreign keys with consistent validation and error messages.
6. **Indexes and query planning** — introduce indexes for common lookup paths,
   then add a simple query plan representation and performance benchmarks.
7. **Network API and security** — expose the database through a protocol or
   service API, with authentication, authorization, encrypted connections,
   resource limits, and query timeouts.
8. **Operational tooling** — add structured logging, metrics, health checks,
   import/export commands, and tools for inspecting active sessions and locks.
9. **CLI improvements** — add command history, multiline statements,
   semicolon-delimited input, configurable output formats, and helpful
   commands such as `.help`, `.tables`, and `.quit`.
