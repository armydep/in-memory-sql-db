import tempfile
import unittest
from pathlib import Path

from memdb.config import load_config


class LoadConfigTest(unittest.TestCase):
    def test_uses_in_memory_defaults_without_a_config_file(self):
        config = load_config()

        self.assertFalse(config.storage.enabled)
        self.assertIsNone(config.storage.path)
        self.assertIsNone(config.storage.implementation)

    def test_loads_storage_settings_from_toml(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "memdb.toml"
            config_path.write_text(
                """
[storage]
enabled = true
path = "./data/memdb.json"
implementation = "memdb.storage.json_file_storage.JsonFileStorage"
""".strip(),
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertTrue(config.storage.enabled)
        self.assertEqual(config.storage.path, Path("./data/memdb.json"))
        self.assertEqual(
            config.storage.implementation,
            "memdb.storage.json_file_storage.JsonFileStorage",
        )


if __name__ == "__main__":
    unittest.main()
