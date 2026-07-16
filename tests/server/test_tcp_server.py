import socket
import threading
import unittest

from memdb.commands.query_factory import QueryFactory
from memdb.dbms import DBMS
from memdb.protocol import decode_result
from memdb.server.tcp_server import DBMSServer, MAX_COMMAND_BYTES
from memdb.storage.in_memory_storage import InMemoryStorage


class DBMSServerTest(unittest.TestCase):
    def setUp(self):
        self.dbms = DBMS(InMemoryStorage(), QueryFactory())
        self.dbms.init()
        self.server = DBMSServer("127.0.0.1", 0, self.dbms)
        self.port = self.server.server_address[1]
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=5)

    def _connect(self) -> socket.socket:
        connection = socket.create_connection(("127.0.0.1", self.port), timeout=5)
        self.addCleanup(connection.close)
        return connection

    @staticmethod
    def _send_command(connection: socket.socket, command: bytes):
        connection.sendall(command)
        reader = connection.makefile("rb")
        try:
            return decode_result(reader.readline())
        finally:
            reader.close()

    def test_executes_queries_against_shared_database(self):
        first = self._connect()
        second = self._connect()

        created = self._send_command(first, b"create table users {id int, name str};")
        inserted = self._send_command(
            second, b'insert (id, name) into users (1, "alice");'
        )
        selected = self._send_command(first, b"select * from users;")

        self.assertTrue(created.success)
        self.assertTrue(inserted.success)
        self.assertEqual(selected.columns, ["id", "name"])
        self.assertEqual(selected.rows, [[1, "alice"]])

    def test_invalid_query_does_not_close_session(self):
        connection = self._connect()
        reader = connection.makefile("rb")
        self.addCleanup(reader.close)

        connection.sendall(b"not sql;")
        self.assertFalse(decode_result(reader.readline()).success)
        connection.sendall(b"describe db;")
        self.assertTrue(decode_result(reader.readline()).success)

    def test_executes_multiple_commands_on_one_connection(self):
        connection = self._connect()
        reader = connection.makefile("rb")
        self.addCleanup(reader.close)

        connection.sendall(
            b"create table users {id int, name str};"
            b'insert (id, name) into users (1, "alice");'
            b"select * from users;"
        )

        self.assertTrue(decode_result(reader.readline()).success)
        self.assertTrue(decode_result(reader.readline()).success)
        selected = decode_result(reader.readline())
        self.assertEqual(selected.rows, [[1, "alice"]])

    def test_invalid_utf8_returns_failure(self):
        result = self._send_command(self._connect(), b"\xff;")

        self.assertFalse(result.success)
        self.assertIn("UTF-8", result.message)

    def test_serves_client_while_another_connection_is_idle(self):
        idle_connection = self._connect()
        active_connection = self._connect()

        response = self._send_command(active_connection, b"describe db;")

        self.assertTrue(response.success)
        idle_connection.close()

    def test_rejects_oversized_command(self):
        result = self._send_command(
            self._connect(), b"x" * (MAX_COMMAND_BYTES + 1) + b";"
        )

        self.assertFalse(result.success)
        self.assertIn("too long", result.message)


if __name__ == "__main__":
    unittest.main()
