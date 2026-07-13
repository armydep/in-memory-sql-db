import unittest
from pathlib import Path
from unittest.mock import patch

from memdb.demo import main
from memdb.storage.json_file_storage import JsonFileStorage


class DemoTest(unittest.TestCase):
    @patch("memdb.demo.print")
    def test_uses_storage_configuration_file(self, _print):
        config_path = Path("memdb.toml.example")

        with patch("memdb.demo.DBMS") as dbms_class:
            main(config_path=config_path)

        storage = dbms_class.call_args.kwargs["storage"]
        self.assertIsInstance(storage, JsonFileStorage)
        self.assertEqual(storage.path, Path("./data/memdb.json"))


if __name__ == "__main__":
    unittest.main()
