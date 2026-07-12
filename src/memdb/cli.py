from collections.abc import Callable
from typing import Any

from memdb import DBMS
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.storage.in_memory_storage import InMemoryStorage

Input = Callable[[str], str]
Output = Callable[[str], Any]


def _format_table(columns: list[str], rows: list[list[Any]]) -> list[str]:
    values = [[str(value) for value in row] for row in rows]
    widths = [
        max(len(column), *(len(row[index]) for row in values))
        if values else len(column)
        for index, column in enumerate(columns)
    ]

    def format_row(row: list[str]) -> str:
        return " | ".join(value.ljust(width) for value, width in zip(row, widths))

    return [
        format_row(columns),
        "-+-".join("-" * width for width in widths),
        *(format_row(row) for row in values),
    ]


def print_result(result: QueryResult, output: Output = print) -> None:
    if not result.success:
        output(f"Error: {result.message or 'query failed'}")
        return

    if result.columns:
        for line in _format_table(result.columns, result.rows):
            output(line)

    if result.message:
        output(result.message)


def run_repl(
    dbms: DBMS,
    input_fn: Input = input,
    output: Output = print,
) -> None:
    output("memdb CLI")
    output("Enter a query, or type 'exit' to quit.")

    while True:
        try:
            query = input_fn("memdb> ").strip()
        except (EOFError, KeyboardInterrupt):
            output("")
            return

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            return

        try:
            print_result(dbms.execute(query), output)
        except ValueError as error:
            output(f"Error: {error}")
        except Exception as error:
            output(f"Unexpected error: {error}")


def main() -> None:
    dbms = DBMS(storage=InMemoryStorage(), query_factory=QueryFactory())
    dbms.init()
    run_repl(dbms)
