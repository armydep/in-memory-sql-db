import argparse
import socket
from collections.abc import Callable
from typing import Any

from memdb.cli import print_result
from memdb.commands.query_result import QueryResult
from memdb.protocol import decode_result
from memdb.query_input import QUERY_DELIMITER, is_exit_command, split_complete_queries

Input = Callable[[str], str]
Output = Callable[[str], Any]

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 7654


class LineClient:
    """TCP client for the semicolon-delimited memdb protocol.

    Sends one SQL command per semicolon; the server returns one JSON-encoded
    QueryResult line for each request.
    """

    def __init__(self, host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT):
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None
        self._reader = None

    def connect(self) -> None:
        self._socket = socket.create_connection((self.host, self.port))
        self._reader = self._socket.makefile("rb")

    def execute(self, command: str) -> QueryResult:
        if self._socket is None or self._reader is None:
            raise RuntimeError("client is not connected")

        command = command.strip()
        if command.endswith(QUERY_DELIMITER):
            command = command[:-1].strip()
        self._socket.sendall(f"{command}{QUERY_DELIMITER}".encode("utf-8"))
        response = self._reader.readline()
        if not response:
            raise ConnectionError("server closed the connection")
        return decode_result(response)

    def close(self) -> None:
        if self._reader is not None:
            self._reader.close()
            self._reader = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def __enter__(self) -> "LineClient":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def run_repl(
    client: LineClient,
    input_fn: Input = input,
    output: Output = print,
) -> None:
    output(f"connected to memdb server at {client.host}:{client.port}")
    output("Enter a query ending with ';', or type 'exit' to quit.")
    buffer = ""

    while True:
        try:
            line = input_fn("...> " if buffer.strip() else "memdb> ")
        except (EOFError, KeyboardInterrupt):
            output("")
            return

        if not line.strip() and not buffer.strip():
            continue
        if is_exit_command(line) and not buffer.strip():
            return

        buffer = f"{buffer}\n{line}" if buffer else line
        queries, buffer = split_complete_queries(buffer)
        for query in queries:
            if is_exit_command(query):
                return

            try:
                print_result(client.execute(query), output)
            except (ConnectionError, OSError) as error:
                output(f"connection lost: {error}")
                return
            except ValueError as error:
                output(f"protocol error: {error}")
                return


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="memdb-client")
    parser.add_argument("--host", default=_DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT)
    args = parser.parse_args(argv)

    with LineClient(args.host, args.port) as client:
        run_repl(client)


if __name__ == "__main__":
    main()
