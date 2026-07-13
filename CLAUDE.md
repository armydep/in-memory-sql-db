# CLAUDE.md

Guidance for AI assistants (Claude Code) working in this repository.

## Project overview

An in-memory relational SQL database written in Python, developed as a
learning project. Currently an embeddable library with an interactive CLI;
persistence and a network server are planned (see the Roadmap in README.md).
It speaks a small **custom SQL dialect** (see Query language below), parsed
by a hand-written parser — not standard SQL.

**Learning is the point of this project, and it is broader than databases.**
The owner is learning, in equal measure:

- how SQL databases / storage engines work internally;
- clean project development (architecture, incremental phases, code review,
  TDD);
- **Python itself** — the language, its idioms, and its OOP model (the owner
  is experienced in software but new to Python);
- the **Python stack and its best practices** — packaging (`pyproject.toml`,
  src-layout, editable installs, entry points), `unittest`/`unittest.mock`,
  dataclasses, ABCs, type hints, stdlib modules (`re`, `shlex`, `argparse`,
  `json`, ...), and eventually the wider ecosystem (HTTP serving, cloud SDKs,
  containers).

Consequences for how the assistant should behave:

- **Explain the "why", not just the "what."** When reviewing or proposing
  code, briefly explain the Python concept or idiom involved, especially
  language-specific behavior that differs from other languages (e.g. `bool`
  subclassing `int`, mutable default arguments, name lookup in
  `unittest.mock.patch`). Small focused examples beat long tutorials.
- **Prefer the idiomatic-Python way and name it** (dataclasses over manual
  `__init__`, context managers, comprehensions, EAFP where it fits), so the
  owner learns what "pythonic" means case by case — but do not refactor
  working code to be more idiomatic uninvited; suggest it in review instead.
- **Understanding beats delivery speed.** A slightly slower path where the
  owner implements and learns is preferred over the assistant implementing
  it for them.

The project owner drives design and implements most features themselves,
often TDD-style. The assistant's default role is mentor/reviewer: propose,
review, explain, and prepare tests — **do not implement features, add
scaffolding, or expand scope unless explicitly asked.** Work one requested
step at a time and stop; do not auto-continue to the next phase.

## Commands

```bash
pip install -e .                          # install (editable); registers the `memdb` script
python -m unittest discover -s tests      # run all tests
python -m unittest tests.commands.test_insert -v   # run one test module
memdb            # interactive SQL REPL (or: python -m memdb)
memdb demo       # scripted demo sequence (or: python -m memdb demo)
```

No runtime dependencies — **standard library only**. Do not add external
packages without the owner's explicit approval (the planned S3 storage
backend is the one anticipated exception).

## Architecture

Execution flow (Command pattern):

```
client → DBMS.execute(sql) → QueryFactory.create(sql) → QueryParser.parse(sql)
       → concrete QueryInterface (one class per statement) → query.run(db_data)
       → QueryResult back to client
```

- `src/memdb/dbms.py` — facade. Requires injected `DBStorage` + `QueryFactory`;
  `data` is `None` until `init()` loads it via `storage.load()`; `execute()`
  raises `RuntimeError` if called before `init()`.
- `src/memdb/commands/` — one file/class per SQL statement implementing
  `QueryInterface.run(data: DBData) -> QueryResult`, plus `QueryFactory`
  (a thin delegate to the parser) and the `QueryResult` dataclass.
- `src/memdb/parser/query_parser.py` — hand-written parser: one regex per
  statement, matched sequentially; constructs command objects directly.
- `src/memdb/data/` — ALL mutable database state, rooted at `DBData`
  (`DBData → Table → Row → Cell → CellData`; `Table → Column → Datatype`).
- `src/memdb/storage/` — `DBStorage` ABC (`load()/save()`); `InMemoryStorage`
  is the no-op placeholder implementation.
- `src/memdb/cli.py` — REPL with injected `input_fn`/`output` for testability.

Accurate diagrams: `docs/class-diagram.md`, `docs/sequence-run-query.md`,
`docs/flowchart-dbms.md` (Mermaid; keep them in sync when structure changes).
`docs/ARCHITECTURE.md` describes the *aspirational* long-term system
(optimizer, indexes, cache) — do not treat it as a map of current code.

## Query language (custom dialect)

Case-insensitive keywords. One statement per line. Supported:

```
describe db
describe table <name>
create table <name> { <col> <TYPE>, ... }     -- TYPE: INT | STR | BOOL (BLOB is rejected, see below)
drop table <name>
select * from <name>
insert (<col>, ...) into <name> (<value>, ...)
delete from <name> where {<col> = <value>}    -- parsed only, run() not implemented
update (<value>, ...) in <name> where {<col> = <value>}   -- parsed only
```

Value literals: unquoted `true`/`false` → bool, decimal integers → int,
`"quoted"` → str (quotes preserved by shlex `posix=False` so that `"true"`
stays a string), anything else → str.

## Conventions and invariants (do not break)

1. **Statement-level failures return `QueryResult(success=False, message=...)`,
   never raise.** Only parse/grammar errors raise (`ValueError` from the
   parser). `run()` methods must not leak exceptions for expected failures.
2. **Construct `QueryResult` with keyword arguments** (`success=`, `message=`,
   `columns=`, `rows=`).
3. **Type checks on cell values use `type(value) is expected_type`, not
   `isinstance`.** `bool` is a subclass of `int` in Python; `isinstance` would
   silently accept `True` in an INT column. Do not "simplify" this.
4. **All mutable database state lives under `DBData`** — never cache rows or
   tables in `DBMS`, commands, the factory, or the parser. Data classes stay
   dumb and serializable (no handles, sockets, callbacks, or back-references).
   This is the precondition for the persistence phase.
5. **`tests/` must NOT contain a `memdb/` directory.** Test subpackages mirror
   `src/memdb/`'s children directly (`tests/commands/`, `tests/parser/`, ...).
   A `tests/memdb/` package shadows the installed `memdb` package during
   `unittest discover` and breaks every import.
6. **BLOB is deliberately rejected at parse time** ("unsupported column type
   Blob"): the value grammar has no bytes literal, so a BLOB column could
   never be populated. `BlobType`/`BlobData` remain in code for the future.
7. **Configuration is read only at the composition root** (`__main__.py` /
   future server startup) and passed down via constructors. No `os.environ`
   reads inside engine classes.
8. **`QueryResult.rows` carries plain Python values**, not `Cell`/`CellData`
   objects (commands unwrap via `cell.data.value()`).
9. Tests use stdlib `unittest` (+ `unittest.mock`), not pytest.

## Git workflow

- Work on `main` (the owner also pushes to it from their machine):
  **always `git fetch origin main` and reconcile before pushing.**
- Never force-push; never rewrite published history.
- Do not create pull requests; commit directly with clear messages.
- Run the full test suite and `python -m memdb demo` before committing.

## Releases

Trunk-based development: releases are **annotated tags on `main`**
(`v1.0.0`, semantic versioning), documented in `CHANGELOG.md`, with the
full step-by-step process and commands in `docs/release-process.md`.
Released tags are immutable — never move, delete, or reuse one. Release
branches (`release/1.x`) are created lazily from the tag only when a
hotfix to an old version is actually needed. `pyproject.toml`'s version
must always match the latest tag.

## Decision record (why things are the way they are)

- Hand-written parser, chosen over a parsing library (learning goal).
- `QueryParser.parse()` returns command objects directly; `QueryFactory` is
  a thin seam kept for a possible second parser strategy.
- INSERT uses named columns + values (`insert (cols) into t (values)`),
  bound into a dict — order-independent by design.
- `CellMetadata` (default value, min/max size) belongs to `Column`, not to
  each `Cell` (memory + consistency).
- Planned persistence: two-section JSON snapshot ({metadata, data} with a
  `version` field), atomic write via temp file + `os.replace`, save after
  every successful mutating command, fail-loudly on corrupt/unknown-version
  snapshots (never silently start empty over an existing file).
