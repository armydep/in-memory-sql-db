import tempfile
import unittest
from pathlib import Path

from memdb.config import ServerConfig, load_config


class ServerConfigTest(unittest.TestCase):
    def _write_config(self, content: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "memdb.toml"
        path.write_text(content, encoding="utf-8")
        return path

    def test_defaults_when_no_config_file(self):
        config = load_config(None)

        self.assertEqual(config.server, ServerConfig(host="127.0.0.1", port=7654))

    def test_defaults_when_file_has_no_server_section(self):
        path = self._write_config('[storage]\nenabled = false\n')

        config = load_config(path)

        self.assertEqual(config.server, ServerConfig(host="127.0.0.1", port=7654))

    def test_reads_host_and_port(self):
        path = self._write_config('[server]\nhost = "0.0.0.0"\nport = 9000\n')

        config = load_config(path)

        self.assertEqual(config.server, ServerConfig(host="0.0.0.0", port=9000))

    def test_rejects_non_integer_port(self):
        path = self._write_config('[server]\nport = "7654"\n')

        with self.assertRaisesRegex(ValueError, "server.port"):
            load_config(path)

    def test_rejects_out_of_range_port(self):
        path = self._write_config("[server]\nport = 70000\n")

        with self.assertRaisesRegex(ValueError, "between 1 and 65535"):
            load_config(path)

    def test_rejects_empty_host(self):
        path = self._write_config('[server]\nhost = ""\n')

        with self.assertRaisesRegex(ValueError, "server.host"):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
