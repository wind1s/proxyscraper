"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause
"""
from typing import Any
from datetime import datetime, timedelta
from diskcache import Cache


class Database:
    """
    Simple database interface. Similar functionality to dictionaries.
    """

    TIME_FORMAT = "%Y/%m/%d %H:%M:%S"

    def __init__(self, path: str) -> None:
        self.__database = Cache(path)

    def __enter__(self):
        return self

    def __exit__(self, *exception) -> None:
        self.close()

    def close(self) -> None:
        """
        Closes the database object.
        """
        self.__database.close()

    def get_entries(self):
        """
        Retrieve a list of all database keys.
        """
        return list(self.__database)

    def get_count(self):
        """
        Retrieve the number of keys in database.
        """
        return len(self.__database)

    def __contains__(self, key: Any) -> bool:
        """
        Checks if an ip address exists as an entry in a database.
        """
        return self.__database is not None and key in self.__database

    def get(self, key: Any) -> Any:
        return self.__database.get(key)

    def key_expired(self, key: Any, expire_time: timedelta) -> bool:
        """
        Checks if an ip address entry has expired according to an expiry time.
        If it does not exist it is considered expired.
        """
        if self.__contains__(key):
            last_entry_time = datetime.strptime(self.get(key)["entry_time"], Database.TIME_FORMAT)
            return (datetime.now() - last_entry_time) >= expire_time

        return True

    def store_entry(self, key: Any, data: dict[Any, Any]) -> None:
        """
        Stores an key with it's data and adds a timestamp
        """
        data["entry_time"] = datetime.now().strftime(Database.TIME_FORMAT)
        self.__database.set(key, data)
