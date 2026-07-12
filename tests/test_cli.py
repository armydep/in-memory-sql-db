import unittest

from memdb import DBMS
from memdb.cli import print_result, run_repl
from memdb.commands.query_factory import QueryFactory
from memdb.commands.query_result import QueryResult
from memdb.storage.in_memory_storage import InMemoryStorage


class PrintResultTest(unittest.TestCase):
    def test_prints_tabular_result(self):
        lines = []
        result = QueryResult(
            success=True,
            message="rows selected",
            columns=["id", "name"],
            rows=[[1, "alice"], [20, "bob"]],
        )

        print_result(result, lines.append)

        self.assertEqual(
            lines,
            [
                "id | name ",
                "---+------",
                "1  | alice",
                "20 | bob  ",
                "rows selected",
            ],
        )

    def test_prints_failed_result_as_error(self):
        lines = []

        print_result(QueryResult(success=False, message="bad query"), lines.append)

        self.assertEqual(lines, ["Error: bad query"])


class RunReplTest(unittest.TestCase):
    def setUp(self):
        self.dbms = DBMS(InMemoryStorage(), QueryFactory())
        self.dbms.init()

    def test_executes_queries_in_the_same_database_until_exit(self):
        queries = iter([
            "create table users {id int, name str}",
            'insert (id, name) into users (1, "alice")',
            "select * from users",
            "exit",
        ])
        lines = []

        run_repl(self.dbms, lambda _prompt: next(queries), lines.append)

        self.assertIn("table users created", lines)
        self.assertIn("1  | alice", lines)
        self.assertEqual(len(self.dbms.data.tables["users"].rows), 1)

    def test_reports_invalid_query_and_continues(self):
        queries = iter(["not sql", "describe db", "quit"])
        lines = []

        run_repl(self.dbms, lambda _prompt: next(queries), lines.append)

        self.assertIn("Error: Unsupported query: not sql", lines)
        self.assertIn("Tables", lines)

    def test_eof_exits_cleanly(self):
        lines = []

        def end_input(_prompt):
            raise EOFError

        run_repl(self.dbms, end_input, lines.append)

        self.assertEqual(lines[-1], "")


if __name__ == "__main__":
    unittest.main()
