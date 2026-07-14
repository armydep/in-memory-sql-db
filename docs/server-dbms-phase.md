# Multi-User TCP Server — Shared DBMS Phase

This phase replaces the echo walking skeleton with a real SQL server. A
single server process initializes one `DBMS`; every connected client executes
against that shared database.

## Design

- `DBMSServer` uses `socketserver.ThreadingTCPServer`, which gives each client
  connection its own thread.
- `DBMS` owns a database-wide lock. Query creation, execution, mutation, and
  any resulting storage save happen inside the same critical section. This
  applies whether persistence is enabled or disabled.
- The lock favors correctness and simplicity. Queries are currently
  serialized, including reads; finer-grained or readers/writer locking can be
  added after behavior and performance justify it.
- One server process must be the sole owner of a JSON snapshot. Separate
  processes do not share the in-process lock.

## Wire protocol

Requests are UTF-8 SQL commands separated by newlines. A request may be at
most 64 KiB. Each response is one UTF-8 JSON line containing the public
`QueryResult` fields:

```json
{"success":true,"message":"table users created","columns":[],"rows":[]}
```

`data_changed` is an internal execution detail and is not sent to clients.
Invalid SQL and malformed UTF-8 produce failed query results; the connection
remains usable. An oversized line produces a failure and closes that session.

## Running locally

```bash
python -m memdb.server --config memdb.toml.example
python -m memdb.client
```

## Running with persistent Docker storage

```bash
docker compose up --build memdb-server
python -m memdb.client
```

Compose binds the service to `127.0.0.1:7654` on the host and mounts the
`memdb-data` named volume at `/data` in the container. The server config stores
the JSON snapshot at `/data/memdb.json`.

## Current limitations

- No authentication, authorization, TLS, transactions, query timeouts, or
  per-client resource quotas.
- No cross-process or distributed locking.
- Graceful shutdown stops accepting new work, but active daemon session
  threads are not drained.
