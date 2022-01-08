"""
Provides functionality to make async http requests.
"""
from typing import Optional, Any, Iterator, Dict, Callable
from itertools import islice
from asyncio import ensure_future, sleep, get_event_loop
from json import loads
from aiohttp import ClientSession
from request import Request


async def async_request(request_data: Request, session: ClientSession) -> Any:
    """
    The standard request which can be customized.
    """
    async with session.request(**request_data) as response:
        return await response.read()


async def async_json_request(request_data: Request, session: ClientSession) -> Dict[str, str]:
    """
    Standard json accept request.
    """
    request_data["headers"] = {"Accept": "application/json"}
    response = await async_request(request_data, session)
    return loads(response)


async def limit_coros(request_coros: Iterator[Any], limit: int) -> Iterator[Any]:
    """
    Runs a limited amount of coroutines at a time. Runs a new coroutine when one finishes.
    """
    futures = [ensure_future(c) for c in islice(request_coros, 0, limit)]
    push_future = futures.append
    remove_future = futures.remove

    while futures:
        await sleep(0)

        for f in futures:
            if f.done():
                remove_future(f)
                newf = next(request_coros, None)

                # If next returns the default value None, there is no more coroutines to run.
                if newf is not None:
                    push_future(ensure_future(newf))

                await f


def run_async_requests(
    requests_data: Iterator[Request],
    async_request: Callable[Any, ClientSession] = async_request,
    base_url: Optional[str] = None,
    limit: Optional[int] = 1000,
) -> None:
    """Creates coroutines for all requests and runs them async."""

    async def launch():
        async with ClientSession(base_url=base_url) as session:
            coros = (async_request(data, session) for data in requests_data)
            return await limit_coros(coros, limit)

    loop = get_event_loop()
    loop.run_until_complete(launch())
    loop.close()
