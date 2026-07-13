import socket
import threading
import unittest

from memdb.server.tcp_server import MAX_LINE_BYTES, EchoServer


class EchoServerTest(unittest.TestCase):
    def setUp(self):
        # Port 0 asks the OS for any free port; the chosen one is read
        # back from server_address, so tests never collide on a port.
        self.server = EchoServer("127.0.0.1", 0)
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
    def _send_line(connection: socket.socket, line: bytes) -> bytes:
        connection.sendall(line)
        reader = connection.makefile("rb")
        try:
            return reader.readline()
        finally:
            reader.close()

    def test_echoes_a_line_back(self):
        connection = self._connect()

        response = self._send_line(connection, b"select * from users\n")

        self.assertEqual(response, b"select * from users\n")

    def test_echoes_multiple_lines_on_one_connection(self):
        connection = self._connect()
        reader = connection.makefile("rb")
        self.addCleanup(reader.close)

        connection.sendall(b"first\n")
        self.assertEqual(reader.readline(), b"first\n")
        connection.sendall(b"second\n")
        self.assertEqual(reader.readline(), b"second\n")

    def test_strips_carriage_return_from_clients_using_crlf(self):
        connection = self._connect()

        response = self._send_line(connection, b"hello\r\n")

        self.assertEqual(response, b"hello\n")

    def test_serves_a_client_while_another_connection_sits_idle(self):
        # With one thread per connection, an idle client must not block
        # others; a sequential accept-then-handle server would hang here.
        idle_connection = self._connect()
        active_connection = self._connect()

        response = self._send_line(active_connection, b"ping\n")

        self.assertEqual(response, b"ping\n")
        idle_connection.close()

    def test_rejects_oversized_line(self):
        connection = self._connect()

        response = self._send_line(connection, b"x" * (MAX_LINE_BYTES + 1) + b"\n")

        self.assertEqual(response, b"error: line too long\n")


if __name__ == "__main__":
    unittest.main()
