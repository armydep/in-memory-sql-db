import socket
import threading
import unittest

from memdb.client import LineClient, run_repl
from memdb.server.tcp_server import EchoServer


class LineClientTest(unittest.TestCase):
    def setUp(self):
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

    def test_send_returns_server_response(self):
        with LineClient("127.0.0.1", self.port) as client:
            self.assertEqual(client.send("hello"), "hello")
            self.assertEqual(client.send("select * from users"),
                             "select * from users")

    def test_send_before_connect_raises(self):
        client = LineClient("127.0.0.1", self.port)

        with self.assertRaisesRegex(RuntimeError, "not connected"):
            client.send("hello")

    def test_repl_sends_lines_and_prints_responses_until_exit(self):
        lines = []
        inputs = iter(["hello there", "", "exit"])

        with LineClient("127.0.0.1", self.port) as client:
            run_repl(client, lambda _prompt: next(inputs), lines.append)

        self.assertIn("hello there", lines)

    def test_repl_reports_lost_connection_and_returns(self):
        lines = []
        inputs = iter(["after disconnect"])

        with LineClient("127.0.0.1", self.port) as client:
            self.assertEqual(client.send("hello"), "hello")
            # shutdown(SHUT_RDWR) actually tears the connection down;
            # socket.close() would not, while the makefile reader still
            # holds the underlying file descriptor open.
            client._socket.shutdown(socket.SHUT_RDWR)

            run_repl(client, lambda _prompt: next(inputs), lines.append)

        self.assertTrue(
            any(line.startswith("connection lost:") for line in lines),
            f"no connection-lost message in {lines!r}",
        )


if __name__ == "__main__":
    unittest.main()
