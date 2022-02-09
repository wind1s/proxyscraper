from typing import Union, IO
from logging import basicConfig, getLogger, Logger
from asynchttprequest import AsyncRequest
from aiohttp import ClientSession, ClientError, http_exceptions
from utility import str_join
from config import DEFAULT_LOG_FILE


def get_default_logger() -> Logger:
    return getLogger(DEFAULT_LOG_FILE)


def init_logger(level: int, stream: IO) -> None:
    basicConfig(
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=level,
        datefmt="%H:%M:%S",
        stream=stream,
    )

    logger = get_default_logger()
    getLogger("chardet.charsetprober").disabled = True
    logger.info("Initialized logger")


async def log_request(request: AsyncRequest, session: ClientSession) -> Union[str, None]:
    log = get_default_logger()
    base_url = session._base_url
    request_full_url = request.url if base_url is None else str_join(str(base_url), request.url)

    try:
        response = await request.send(session)

    except (
        ClientError,
        http_exceptions.HttpProcessingError,
    ) as e:
        log.error(
            "aiohttp exception for %s [%s]: %s",
            request_full_url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )
        return None

    except Exception as e:
        log.exception("Non-aiohttp exception occured: %s", getattr(e, "__dict__", {}))
        return None

    log.debug("Got response from %s", request_full_url)
    return response


def log_db_entry_status(entry_count_diff: int, db_name: str) -> None:
    log = get_default_logger()

    if entry_count_diff > 0:
        log.info("%d new entries in cache %s", entry_count_diff, db_name)
    else:
        log.info("No new entries in cache %s", db_name)
