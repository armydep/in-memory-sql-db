import unittest
from unittest.mock import patch

from memdb.__main__ import main


class MainTest(unittest.TestCase):
    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_cli_is_the_default_mode(self, cli_main, demo_main):
        main([])

        cli_main.assert_called_once_with()
        demo_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_cli_mode_starts_cli(self, cli_main, demo_main):
        main(["cli"])

        cli_main.assert_called_once_with()
        demo_main.assert_not_called()

    @patch("memdb.__main__.demo_main")
    @patch("memdb.__main__.cli_main")
    def test_demo_mode_runs_original_demo(self, cli_main, demo_main):
        main(["demo"])

        demo_main.assert_called_once_with()
        cli_main.assert_not_called()


if __name__ == "__main__":
    unittest.main()
