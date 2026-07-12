# in-memory-sql-db

An in-memory relational SQL database, built as an embeddable Python library
(no network server in this phase).

## Status

Repository scaffold: package structure and class skeletons only. Statement
parsing and execution logic are implemented incrementally in later steps.

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
