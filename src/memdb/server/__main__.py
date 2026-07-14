import argparse
import logging
import signal
from pathlib import Path
from types import FrameType

from memdb.commands.query_factory import QueryFactory
from memdb.config import load_config
from memdb.dbms import DBMS
from memdb.server.tcp_server import DBMSServer
from memdb.setup_logging import log_storage_setup
from memdb.storage.factory import create_storage

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
        help="path to a TOML configuration file with [server] and [storage] sections",
    )
    args = parser.parse_args(argv)

    # Startup failures (missing/invalid config, corrupt snapshot) are
    # operator errors, not bugs: report one line and a non-zero exit
    # instead of a traceback.
    try:
        config = load_config(args.config)
        storage = create_storage(config.storage)
        log_storage_setup(args.config, config.storage, storage)
        dbms = DBMS(storage=storage, query_factory=QueryFactory())
        dbms.init()
    except (ValueError, OSError) as error:
        logger.error("startup failed: %s", error)
        raise SystemExit(1) from error

    def request_shutdown(signum: int, frame: FrameType | None) -> None:
        raise SystemExit(0)

    # docker stop sends SIGTERM; without a handler the process dies
    # immediately instead of closing the listening socket first.
    signal.signal(signal.SIGTERM, request_shutdown)

    with DBMSServer(config.server.host, config.server.port, dbms) as server:
        logger.info(
            "memdb server listening on %s:%d", config.server.host, config.server.port
        )
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("shutting down")


if __name__ == "__main__":
    main()
