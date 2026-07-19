import argparse
import statistics
from time import perf_counter

from memdb.client import LineClient
from memdb.commands.query_result import QueryResult


def _execute_or_fail(client: LineClient, command: str) -> QueryResult:
    result = client.execute(command)
    if not result.success:
        raise RuntimeError(f"{command!r} failed: {result.message}")
    return result


def _drop_table_if_exists(client: LineClient, table_name: str) -> None:
    client.execute(f"drop table {table_name}")


def _load_table(
    client: LineClient,
    table_name: str,
    rows: int,
    with_index: bool,
) -> float:
    index_clause = ", index (id)" if with_index else ""
    _drop_table_if_exists(client, table_name)
    _execute_or_fail(
        client,
        f"create table {table_name} {{ id int, email str{index_clause} }}",
    )

    start = perf_counter()
    for row_id in range(rows):
        email = f"user{row_id}@example.com"
        _execute_or_fail(
            client,
            f'insert (id, email) into {table_name} ({row_id}, "{email}")',
        )
    return perf_counter() - start


def _measure_query(
    client: LineClient,
    command: str,
    repeats: int,
) -> tuple[list[float], QueryResult]:
    durations = []
    last_result = QueryResult(success=False)
    for _ in range(repeats):
        start = perf_counter()
        last_result = _execute_or_fail(client, command)
        durations.append(perf_counter() - start)
    return durations, last_result


def _summarize(name: str, durations: list[float]) -> None:
    ordered = sorted(durations)
    p95_index = int((len(ordered) - 1) * 0.95)
    print(
        f"{name}: "
        f"runs={len(durations)} "
        f"min={min(durations):.6f}s "
        f"avg={statistics.fmean(durations):.6f}s "
        f"p95={ordered[p95_index]:.6f}s "
        f"max={max(durations):.6f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an end-to-end memdb client/server index benchmark."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7654)
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--lookup-repeats", type=int, default=50)
    parser.add_argument("--scan-repeats", type=int, default=3)
    parser.add_argument("--indexed-table", default="bench_indexed")
    parser.add_argument("--plain-table", default="bench_plain")
    args = parser.parse_args()

    if args.rows <= 0:
        raise SystemExit("--rows must be positive")
    if args.lookup_repeats <= 0:
        raise SystemExit("--lookup-repeats must be positive")
    if args.scan_repeats <= 0:
        raise SystemExit("--scan-repeats must be positive")

    target_id = args.rows // 2
    with LineClient(args.host, args.port) as client:
        print(f"connected to memdb server at {args.host}:{args.port}")
        print(f"loading {args.rows} rows into {args.indexed_table} with index(id)")
        indexed_insert_seconds = _load_table(
            client, args.indexed_table, args.rows, with_index=True
        )
        print(
            f"indexed insert: total={indexed_insert_seconds:.6f}s "
            f"rows_per_sec={args.rows / indexed_insert_seconds:.2f}"
        )

        print(f"loading {args.rows} rows into {args.plain_table} without indexes")
        plain_insert_seconds = _load_table(
            client, args.plain_table, args.rows, with_index=False
        )
        print(
            f"plain insert: total={plain_insert_seconds:.6f}s "
            f"rows_per_sec={args.rows / plain_insert_seconds:.2f}"
        )

        indexed_lookup, indexed_result = _measure_query(
            client,
            f"select * from {args.indexed_table} where id == {target_id}",
            args.lookup_repeats,
        )
        plain_lookup, plain_result = _measure_query(
            client,
            f"select * from {args.plain_table} where id == {target_id}",
            args.lookup_repeats,
        )
        full_scan, scan_result = _measure_query(
            client,
            f"select * from {args.indexed_table}",
            args.scan_repeats,
        )

    print(f"lookup target id: {target_id}")
    print(f"indexed lookup rows returned: {len(indexed_result.rows)}")
    print(f"plain lookup rows returned: {len(plain_result.rows)}")
    print(f"full scan rows returned: {len(scan_result.rows)}")
    _summarize("indexed equality lookup", indexed_lookup)
    _summarize("plain equality lookup", plain_lookup)
    _summarize("indexed full scan", full_scan)


if __name__ == "__main__":
    main()
