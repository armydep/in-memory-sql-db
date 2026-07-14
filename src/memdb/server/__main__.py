import argparse
import logging
import signal
from pathlib import Path
from types import FrameType

from memdb.commands.query_factory import QueryFactory
from memdb.config import load_config
from memdb.dbms import DBMS
from memdb.server.config import load_server_config
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
        help="path to a TOML configuration file with a [server] section",
    )
    args = parser.parse_args(argv)
    server_config = load_server_config(args.config)
    app_config = load_config(args.config)
    storage = create_storage(app_config.storage)
    log_storage_setup(args.config, app_config.storage, storage)
    dbms = DBMS(storage=storage, query_factory=QueryFactory())
    dbms.init()

    def request_shutdown(signum: int, frame: FrameType | None) -> None:
        raise SystemExit(0)

    # docker stop sends SIGTERM; without a handler the process dies
    # immediately instead of closing the listening socket first.
    signal.signal(signal.SIGTERM, request_shutdown)

    with DBMSServer(server_config.host, server_config.port, dbms) as server:
        logger.info(
            "memdb server listening on %s:%d", server_config.host, server_config.port
        )
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info("shutting down")


if __name__ == "__main__":
    main()
