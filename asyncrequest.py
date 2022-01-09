from typing import Any, Dict
from aiohttp import ClientSession
from json import loads


class AsyncRequest:
    def __init__(self, method: str, url: str, **kwargs: Any):
        self.method: str = method
        self.url: str = url
        self.__data: Dict[str, str] = {"method": self.method, "url": self.url, **kwargs}

    def __getitem__(self, key: str) -> str:
        return self.__data[str]

    def __setitem__(self, key, value) -> None:
        if key == "method":
            self.method = value
        elif key == "url":
            self.url = value

        self.__data[key] = value

    async def send(self, session: ClientSession, **extra_data) -> str:
        async with session.request(**self.__data, **extra_data) as response:
            return await response.read()

    async def accept_json(self, session: ClientSession) -> Dict[str, str]:
        """
        Standard json accept request.
        """
        response = await self.send(session, headers={"Accept": "application/json"})
        return loads(response)
