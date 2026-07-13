import argparse
import socket
from collections.abc import Callable
from typing import Any

Input = Callable[[str], str]
Output = Callable[[str], Any]

_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 7654


class LineClient:
    """TCP client for the newline-delimited memdb protocol.

    Sends one line per request and reads one line per response. In the
    echo phase the response is the request itself; later phases return a
    JSON-encoded QueryResult over the same framing.
    """

    def __init__(self, host: str = _DEFAULT_HOST, port: int = _DEFAULT_PORT):
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None
        self._reader = None

    def connect(self) -> None:
        self._socket = socket.create_connection((self.host, self.port))
        self._reader = self._socket.makefile("r", encoding="utf-8", newline="\n")

    def send(self, line: str) -> str:
        if self._socket is None or self._reader is None:
            raise RuntimeError("client is not connected")

        self._socket.sendall(f"{line}\n".encode("utf-8"))
        response = self._reader.readline()
        if not response:
            raise ConnectionError("server closed the connection")
        return response.rstrip("\n")

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
    output("Enter a message, or type 'exit' to quit.")

    while True:
        try:
            line = input_fn("memdb> ").strip()
        except (EOFError, KeyboardInterrupt):
            output("")
            return

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            return

        try:
            output(client.send(line))
        except (ConnectionError, OSError) as error:
            output(f"connection lost: {error}")
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
