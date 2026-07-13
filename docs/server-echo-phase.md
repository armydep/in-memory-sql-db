# Multi-User Server — Echo Phase (Walking Skeleton)

First increment of the multi-user roadmap item: a thread-per-connection
TCP server and a line-based client, with the **echo protocol as a
placeholder** — every line a client sends comes straight back. The DBMS,
storage, and CLI are deliberately untouched.

## Why echo first

This is a *walking skeleton*: the thinnest end-to-end slice that
exercises every structural piece — listening socket, one thread per
client, session ids, newline framing, oversized-line guard, client
library, graceful shutdown, Docker port publishing — while the actual
database behavior stays out of the picture. Every piece here survives
unchanged into the real server; only the echo line gets replaced by
parse/execute against the shared `DBMS`.

## Pieces

| Piece | Where |
|---|---|
| `EchoServer` (`socketserver.ThreadingTCPServer`, one thread per client) | `src/memdb/server/tcp_server.py` |
| Server runner with SIGTERM/SIGINT shutdown | `src/memdb/server/__main__.py` |
| `[server]` config (`host`, `port`) | `src/memdb/server/config.py` |
| `LineClient` + client REPL | `src/memdb/client.py` |
| Tests (server, client, config) | `tests/server/`, `tests/test_client.py` |

## Protocol (this phase)

- Requests: UTF-8 lines, one request per line (`\n`-delimited; `\r\n`
  tolerated). Maximum line length 64 KiB — longer requests get
  `error: line too long` and the connection closes.
- Responses: the request line echoed back. Later phases keep the framing
  and replace the payload with a one-line JSON `QueryResult`.
- A connection is a session; the server assigns each one an id used in
  its logs.

## Running locally

```bash
python -m memdb.server                       # 127.0.0.1:7654 (defaults)
python -m memdb.server --config memdb.toml   # host/port from [server]

python -m memdb.client                       # connect to 127.0.0.1:7654
python -m memdb.client --host 127.0.0.1 --port 7654
```

Type lines at the `memdb>` prompt; each comes back echoed. `exit`,
`quit`, Ctrl-D, or Ctrl-C leaves.

## Running in Docker

```bash
docker compose up memdb-server        # publishes 7654 on the host
python -m memdb.client                # from the host, in another shell
```

The `memdb-server` service reuses the same image and named volume as the
interactive `memdb` service; its baked config listens on `0.0.0.0` so the
published port is reachable. `docker stop` sends SIGTERM, which the
server catches to shut down cleanly.

## Deliberately not in this phase

- No wiring to `DBMS`/storage (echo only; existing code unmodified).
- No locking — comes with the real server, per the agreed design
  (readers-writer lock, `mutates` classification per command).
- No JSON responses, no auth, no transactions.
- Only one server process may ever use a given JSON snapshot; running
  the `memdb` CLI service against the volume while `memdb-server` is
  live will be unsafe once the server actually opens the database —
  acceptable during the echo phase, resolved before the real one.
