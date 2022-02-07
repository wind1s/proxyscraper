from typing import Union, IO
from logging import Logger, basicConfig, getLogger, DEBUG
from asynchttprequest import AsyncRequest
from aiohttp import ClientSession, ClientError, http_exceptions


def init_logger(log_name: str, stream: IO):
    basicConfig(
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=DEBUG,
        datefmt="%H:%M:%S",
        stream=stream,
    )

    logger = getLogger(log_name)
    getLogger("chardet.charsetprober").disabled = True

    return logger


async def log_request(
    request: AsyncRequest, session: ClientSession, logger: Logger
) -> Union[str, None]:
    response = None

    try:
        response = await request.send(session)

    except (
        ClientError,
        http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            request.url if session._base_url is None else session._base_url + request.url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )

    except Exception as e:
        logger.exception("Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {}))

    return response
