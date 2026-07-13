import unittest
from pathlib import Path

from memdb.config import StorageConfig
from memdb.storage.factory import create_storage
from memdb.storage.in_memory_storage import InMemoryStorage
from memdb.storage.json_file_storage import JsonFileStorage


class CreateStorageTest(unittest.TestCase):
    def test_returns_in_memory_storage_when_disabled(self):
        storage = create_storage(StorageConfig(enabled=False))

        self.assertIsInstance(storage, InMemoryStorage)

    def test_constructs_configured_storage_implementation(self):
        path = Path("data/memdb.json")

        storage = create_storage(
            StorageConfig(
                enabled=True,
                path=path,
                implementation=(
                    "memdb.storage.json_file_storage.JsonFileStorage"
                ),
            )
        )

        self.assertIsInstance(storage, JsonFileStorage)
        self.assertEqual(storage.path, path)

    def test_requires_path_when_enabled(self):
        with self.assertRaisesRegex(ValueError, "storage.path is required"):
            create_storage(
                StorageConfig(enabled=True, implementation="some.Storage")
            )

    def test_rejects_class_that_does_not_implement_storage_interface(self):
        with self.assertRaisesRegex(TypeError, "does not implement DBStorage"):
            create_storage(
                StorageConfig(
                    enabled=True,
                    path=Path("data/memdb.json"),
                    implementation="pathlib.Path",
                )
            )


if __name__ == "__main__":
    unittest.main()
