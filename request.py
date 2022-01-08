from typing import Any, Dict


class Request:
    def __init__(self, method: str, url: str, **kwargs):
        self.method: str = method
        self.url: str = url
        self.__data: Dict[Any, Any] = {"method": self.method, "url": self.url, **kwargs}

    def __getitem__(self, key: Any) -> Any:
        return self.__data[key]

    def __setitem__(self, key, value) -> None:
        if key == "method":
            self.method = value
        elif key == "url":
            self.url = value

        self.__data[key] = value

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()
