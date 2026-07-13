# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-13

First stable release: an in-memory SQL database as an embeddable Python
library with an interactive CLI. No persistence — data lives for the
lifetime of the process.

### Added

- Custom SQL dialect with a hand-written parser (case-insensitive keywords):
  - `describe db` — list tables
  - `describe table <name>` — show a table's columns and types
  - `create table <name> { <col> <TYPE>, ... }` — types: `INT`, `STR`, `BOOL`
  - `drop table <name>`
  - `select * from <name>`
  - `insert (<col>, ...) into <name> (<value>, ...)` — named columns,
    type-checked against the schema (including strict `bool`/`int` separation)
- Command-pattern execution engine: `DBMS` facade with explicit `init()`
  lifecycle, `QueryFactory`/`QueryParser`, one command class per statement,
  uniform `QueryResult` (success flag, message, columns, rows)
- Interactive CLI (`memdb` / `python -m memdb`) with aligned table output,
  plus a scripted demo mode (`memdb demo`)
- `DBStorage` abstraction with `InMemoryStorage` placeholder (persistence
  seam for a future release)
- Test suite (48 tests, stdlib `unittest`), design diagrams under `docs/`

### Known limitations

- `delete` and `update` statements are parsed but not executed yet
- `BLOB` column type is rejected at parse time (no bytes literal syntax)
- No persistence, no `WHERE` on `select`, single-user only
