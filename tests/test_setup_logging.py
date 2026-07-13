import tempfile
import unittest
from pathlib import Path

from memdb.config import StorageConfig
from memdb.storage.in_memory_storage import InMemoryStorage
from memdb.setup_logging import log_storage_setup


class StorageSetupLoggingTest(unittest.TestCase):
    def test_logs_all_storage_details_with_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config" / "memdb.toml"
            storage_path = root / "data" / "memdb.json"

            with self.assertLogs(
                "memdb.setup_logging", level="INFO"
            ) as captured:
                log_storage_setup(
                    config_path=config_path,
                    config=StorageConfig(
                        enabled=True,
                        path=storage_path,
                        implementation="example.JsonStorage",
                    ),
                    storage=InMemoryStorage(),
                )

        self.assertEqual(len(captured.output), 1)
        message = captured.output[0]
        self.assertIn(f"config={config_path.resolve()}", message)
        self.assertIn("enabled=True", message)
        self.assertIn("mode=persistent", message)
        self.assertIn(f"path={storage_path.resolve()}", message)
        self.assertIn("configured_implementation=example.JsonStorage", message)
        self.assertIn(
            "selected_implementation=memdb.storage.in_memory_storage.InMemoryStorage",
            message,
        )

    def test_logs_in_memory_defaults(self):
        with self.assertLogs(
            "memdb.setup_logging", level="INFO"
        ) as captured:
            log_storage_setup(
                config_path=None,
                config=StorageConfig(enabled=False),
                storage=InMemoryStorage(),
            )

        message = captured.output[0]
        self.assertIn("config=<defaults>", message)
        self.assertIn("mode=in-memory", message)
        self.assertIn("path=<none>", message)
