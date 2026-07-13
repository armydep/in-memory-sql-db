import argparse
import logging
from pathlib import Path

from memdb.cli import main as cli_main
from memdb.demo import main as demo_main


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(prog="memdb")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("cli", "demo"),
        default="cli",
        help="start the interactive CLI (default) or run the built-in demo",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="path to a TOML configuration file",
    )
    args = parser.parse_args(argv)

    if args.mode == "demo":
        demo_main(config_path=args.config)
    else:
        cli_main(config_path=args.config)


if __name__ == "__main__":
    main()
