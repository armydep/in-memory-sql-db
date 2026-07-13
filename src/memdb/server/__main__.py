import argparse
import logging
import signal
from pathlib import Path
from types import FrameType

from memdb.server.config import load_server_config
from memdb.server.tcp_server import EchoServer

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(prog="memdb-server")
    parser.add_argument(
        "--config",
        type=Path,
        help="path to a TOML configuration file with a [server] section",
    )
    args = parser.parse_args(argv)
    config = load_server_config(args.config)

    def request_shutdown(signum: int, frame: FrameType | None) -> None:
        raise SystemExit(0)

    # docker stop sends SIGTERM; without a handler the process dies
    # immediately instead of closing the listening socket first.
    signal.signal(signal.SIGTERM, request_shutdown)

    with EchoServer(config.host, config.port) as server:
        logger.info("echo server listening on %s:%d", config.host, config.port)
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("shutting down")


if __name__ == "__main__":
    main()
