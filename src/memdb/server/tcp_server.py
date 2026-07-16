import logging
import socketserver
from itertools import count

from memdb.commands.query_result import QueryResult
from memdb.dbms import DBMS
from memdb.protocol import encode_result
from memdb.query_input import QUERY_DELIMITER

logger = logging.getLogger(__name__)

# Requests are semicolon-delimited commands; a client that never sends a semicolon
# must not grow the server's buffer forever.
MAX_COMMAND_BYTES = 64 * 1024


class QueryRequestHandler(socketserver.StreamRequestHandler):
    """Execute semicolon-delimited SQL against the server's shared DBMS."""

    def handle(self) -> None:
        session_id = self.server.next_session_id()
        logger.info(
            "session %d connected from %s:%d", session_id, *self.client_address
        )

        command = bytearray()
        while True:
            next_byte = self.rfile.read(1)
            if not next_byte:
                break
            if next_byte == QUERY_DELIMITER.encode("utf-8"):
                self._execute_command(bytes(command), session_id)
                command.clear()
                continue

            command.extend(next_byte)
            if len(command) > MAX_COMMAND_BYTES:
                logger.warning("session %d sent an oversized command", session_id)
                self.wfile.write(
                    encode_result(
                        QueryResult(success=False, message="request command is too long")
                    )
                )
                break

        logger.info("session %d disconnected", session_id)

    def _execute_command(self, command_bytes: bytes, session_id: int) -> None:
        try:
            command = command_bytes.decode("utf-8").strip()
            if not command:
                return
            result = self.server.dbms.execute(command, session_id=session_id)
        except UnicodeDecodeError:
            result = QueryResult(success=False, message="request must be valid UTF-8")
        except ValueError as error:
            result = QueryResult(success=False, message=str(error))
        except Exception:
            logger.exception("session %d query execution failed", session_id)
            result = QueryResult(success=False, message="internal server error")

        self.wfile.write(encode_result(result))


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
