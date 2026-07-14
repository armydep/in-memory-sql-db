import socket
import threading
import unittest

from memdb.client import LineClient, run_repl
from memdb.commands.query_factory import QueryFactory
from memdb.dbms import DBMS
from memdb.server.tcp_server import DBMSServer
from memdb.storage.in_memory_storage import InMemoryStorage


class LineClientTest(unittest.TestCase):
    def setUp(self):
        dbms = DBMS(InMemoryStorage(), QueryFactory())
        dbms.init()
        self.server = DBMSServer("127.0.0.1", 0, dbms)
        self.port = self.server.server_address[1]
        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=5)

    def test_execute_returns_query_result(self):
        with LineClient("127.0.0.1", self.port) as client:
            result = client.execute("describe db")

        self.assertTrue(result.success)
        self.assertEqual(result.columns, ["Tables"])

    def test_execute_before_connect_raises(self):
        client = LineClient("127.0.0.1", self.port)

        with self.assertRaisesRegex(RuntimeError, "not connected"):
            client.execute("describe db")

    def test_repl_executes_queries_and_formats_results(self):
        lines = []
        inputs = iter([
            "create table users {id int, name str}",
            'insert (id, name) into users (1, "alice")',
            "select * from users",
            "exit",
        ])

        with LineClient("127.0.0.1", self.port) as client:
            run_repl(client, lambda _prompt: next(inputs), lines.append)

        self.assertIn("table users created", lines)
        self.assertIn("1  | alice", lines)

    def test_repl_reports_lost_connection_and_returns(self):
        lines = []
        inputs = iter(["describe db"])

        with LineClient("127.0.0.1", self.port) as client:
            client._socket.shutdown(socket.SHUT_RDWR)
            run_repl(client, lambda _prompt: next(inputs), lines.append)

        self.assertTrue(
            any(line.startswith("connection lost:") for line in lines),
            f"no connection-lost message in {lines!r}",
        )


if __name__ == "__main__":
    unittest.main()
