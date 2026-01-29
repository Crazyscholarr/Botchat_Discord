from loguru import logger
import urllib3
import sys
import asyncio
from process import start
import logging


async def main():
    configuration()
    await start()

log_format = (
    "<cyan>[{time:HH:mm:ss | DD-MM-YYYY}]</cyan> "
    "<magenta>[Crazyscholar @ Discord]</magenta> "
    "<level>[{level}]</level> | "
    "<level>{message}</level>"
)


def configuration():
    urllib3.disable_warnings()
    logger.remove()

    # Tắt log của primp và web3
    logging.getLogger("primp").setLevel(logging.WARNING)
    logging.getLogger("web3").setLevel(logging.WARNING)

    logger.add(
        sys.stdout,
        colorize=True,
        format=log_format,
        level="INFO"
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 month",
        format="[ {time:HH:mm:ss | DD-MM-YYYY} ] [ Crazyscholar @ Discord ] [ {level} ] | {message}",
        level="INFO"
    )

if __name__ == "__main__":
    asyncio.run(main())
