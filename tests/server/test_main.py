import tempfile
import unittest
from pathlib import Path

from memdb.server.__main__ import main


class ServerMainStartupTest(unittest.TestCase):
    def test_missing_config_file_exits_nonzero_without_traceback(self):
        with self.assertRaises(SystemExit) as context:
            main(["--config", "does-not-exist.toml"])

        self.assertEqual(context.exception.code, 1)

    def test_corrupt_snapshot_exits_nonzero_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "memdb.json"
            snapshot.write_text("{broken", encoding="utf-8")
            config = Path(directory) / "memdb.toml"
            config.write_text(
                "[storage]\n"
                "enabled = true\n"
                f'path = "{snapshot}"\n'
                'implementation = "memdb.storage.json_file_storage.JsonFileStorage"\n',
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as context:
                main(["--config", str(config)])

            self.assertEqual(context.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
