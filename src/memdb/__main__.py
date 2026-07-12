import argparse

from memdb.cli import main as cli_main
from memdb.demo import main as demo_main


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="memdb")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("cli", "demo"),
        default="cli",
        help="start the interactive CLI (default) or run the built-in demo",
    )
    args = parser.parse_args(argv)

    if args.mode == "demo":
        demo_main()
    else:
        cli_main()


if __name__ == "__main__":
    main()
