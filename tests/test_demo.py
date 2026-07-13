import unittest
from pathlib import Path
from unittest.mock import patch

from memdb.demo import main
from memdb.storage.in_memory_storage import InMemoryStorage
from memdb.storage.json_file_storage import JsonFileStorage


class DemoTest(unittest.TestCase):
    @patch("memdb.demo.print")
    @patch("memdb.demo.log_storage_setup")
    def test_logs_in_memory_storage_setup(self, log_storage_setup, _print):
        main()

        log_storage_setup.assert_called_once()
        arguments = log_storage_setup.call_args.kwargs
        self.assertIsNone(arguments["config_path"])
        self.assertFalse(arguments["config"].enabled)
        self.assertIsInstance(arguments["storage"], InMemoryStorage)

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
