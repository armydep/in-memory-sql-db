import logging
import socketserver
from itertools import count

from memdb.commands.query_result import QueryResult
from memdb.dbms import DBMS
from memdb.protocol import encode_result

logger = logging.getLogger(__name__)

# Requests are newline-delimited lines; a client that never sends a newline
# must not grow the server's buffer forever.
MAX_LINE_BYTES = 64 * 1024


class QueryRequestHandler(socketserver.StreamRequestHandler):
    """Execute newline-delimited SQL against the server's shared DBMS."""

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
                self.wfile.write(
                    encode_result(
                        QueryResult(success=False, message="request line is too long")
                    )
                )
                break

            try:
                command = line.rstrip(b"\r\n").decode("utf-8")
                result = self.server.dbms.execute(command, session_id=session_id)
            except UnicodeDecodeError:
                result = QueryResult(success=False, message="request must be valid UTF-8")
            except ValueError as error:
                result = QueryResult(success=False, message=str(error))
            except Exception:
                logger.exception("session %d query execution failed", session_id)
                result = QueryResult(success=False, message="internal server error")

            self.wfile.write(encode_result(result))

        logger.info("session %d disconnected", session_id)


class DBMSServer(socketserver.ThreadingTCPServer):
    """Thread-per-connection TCP server: one thread per accepted client."""

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, host: str, port: int, dbms: DBMS) -> None:
        super().__init__((host, port), QueryRequestHandler)
        self.dbms = dbms
        self._session_ids = count(1)

    def next_session_id(self) -> int:
        return next(self._session_ids)
