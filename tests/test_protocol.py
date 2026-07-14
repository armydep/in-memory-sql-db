import unittest

from memdb.commands.query_result import QueryResult
from memdb.protocol import decode_result, encode_result


class ProtocolTest(unittest.TestCase):
    def test_query_result_round_trip(self):
        original = QueryResult(
            success=True,
            message="2 rows",
            columns=["id", "name", "payload"],
            rows=[[1, "Alice", b"\x00\xff"], [2, "Bob", b""]],
            data_changed=True,
        )

        decoded = decode_result(encode_result(original))

        self.assertEqual(decoded.success, original.success)
        self.assertEqual(decoded.message, original.message)
        self.assertEqual(decoded.columns, original.columns)
        self.assertEqual(decoded.rows, original.rows)
        self.assertFalse(decoded.data_changed)

    def test_rejects_invalid_json(self):
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            decode_result("not json")

    def test_rejects_invalid_shape(self):
        with self.assertRaisesRegex(ValueError, "columns"):
            decode_result('{"success":true,"message":null,"columns":1,"rows":[]}')


if __name__ == "__main__":
    unittest.main()
