from typing import Any, Dict
from datetime import datetime, timedelta
from diskcache import Cache


class Database:
    TIME_FORMAT = "%Y/%m/%d %H:%M:%S"

    def __init__(self, path: str) -> None:
        self.database = Cache(path)

    def __enter__(self):
        return self

    def __exit__(self, *exception) -> None:
        self.close()

    def close(self) -> None:
        """Closes the database object."""
        self.database.close()

    def __contains__(self, key: Any) -> bool:
        """Checks if an ip address exists as an entry in a database."""
        return self.database != None and key in self.database

    def get(self, key: Any) -> Any:
        return self.database.get(key)

    def key_expired(self, key: Any, expire_time: timedelta) -> bool:
        """
        Checks if an ip address entry has expired according to an expiry time.
        If it does not exist at all it counts as being expired.
        """
        if self.__contains__(key):
            last_entry_time = datetime.strptime(self.get(key)["entry_time"], Database.TIME_FORMAT)
            return (datetime.now() - last_entry_time) >= expire_time

        return True

    def store_entry(self, key: Any, data: Dict[Any, Any]) -> None:
        """
        Stores an key with it's data and adds a timestamp
        """
        data["entry_time"] = datetime.now().strftime(Database.TIME_FORMAT)
        self.database.set(key, data)
