import logging
import socketserver
from itertools import count

logger = logging.getLogger(__name__)

# Requests are newline-delimited lines; a client that never sends a newline
# must not grow the server's buffer forever.
MAX_LINE_BYTES = 64 * 1024


class EchoRequestHandler(socketserver.StreamRequestHandler):
    """Handle one client connection: echo every received line back.

    Placeholder protocol for the multi-user phase: it exercises the full
    connection lifecycle (accept, session, line framing, disconnect)
    without touching the DBMS. Later phases replace the echo with
    parse/execute against the shared database.
    """

    def handle(self) -> None:
        session_id = self.server.next_session_id()
        logger.info(
            "session %d connected from %s:%d", session_id, *self.client_address
        )

        while True:
            line = self.rfile.readline(MAX_LINE_BYTES + 1)
            if not line:
                break
            if len(line) > MAX_LINE_BYTES:
                logger.warning("session %d sent an oversized line", session_id)
                self.wfile.write(b"error: line too long\n")
                break

            self.wfile.write(line.rstrip(b"\r\n") + b"\n")

        logger.info("session %d disconnected", session_id)


class EchoServer(socketserver.ThreadingTCPServer):
    """Thread-per-connection TCP server: one thread per accepted client."""

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, host: str, port: int) -> None:
        super().__init__((host, port), EchoRequestHandler)
        self._session_ids = count(1)

    def next_session_id(self) -> int:
        return next(self._session_ids)
