import unittest
from unittest.mock import patch

from memdb.__main__ import main


class MainTest(unittest.TestCase):
    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_cli_is_the_default_mode(self, cli_main, demo_main):
        main([])

        cli_main.assert_called_once_with(config_path=None)
        demo_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_cli_mode_starts_cli(self, cli_main, demo_main):
        main(["cli"])

        cli_main.assert_called_once_with(config_path=None)
        demo_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_demo_mode_runs_original_demo(self, cli_main, demo_main):
        main(["demo"])

        demo_main.assert_called_once_with(config_path=None)
        cli_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_passes_config_path_to_demo(self, cli_main, demo_main):
        main(["demo", "--config", "memdb.toml"])

        demo_main.assert_called_once()
        self.assertEqual(str(demo_main.call_args.kwargs["config_path"]), "memdb.toml")
        cli_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_passes_config_path_to_cli(self, cli_main, demo_main):
        main(["--config", "memdb.toml"])

        cli_main.assert_called_once()
        self.assertEqual(str(cli_main.call_args.kwargs["config_path"]), "memdb.toml")
        demo_main.assert_not_called()


if __name__ == "__main__":
    unittest.main()
