#!/usr/local/env python3
"""
Retrieves general ip information such as city, region, country,
coordinates, origin and timezone.

Links:
    https://ipinfo.io/ (example in bash: curl ipinfo.io/{ipaddr})

Json layout:
    All values are strings
    {
        'ip':
        'hostname':
        'city':
        'region':
        'country':
        'loc':
        'org':
        'postal':
        'timezone':
        'readme': 'https://ipinfo.io/missingauth'
    }
"""
from typing import Dict, Callable
from datetime import timedelta
from itertools import islice
from aiohttp import ClientSession
from asynchttprequest import run_async_requests
from utility import extract_keys, extract_ip
from database import Database
from asyncrequest import AsyncRequest

IP_DB_NAME = "ip.db"
IP_DB_PATH = f"{IP_DB_NAME}"
IP_DB_EXPIRE_TIME = timedelta(days=365)
IP_INFO_RESPONSE_KEYS = (
    "hostname",
    "city",
    "region",
    "country",
    "loc",
    "org",
    "postal",
    "timezone",
)


async def get_ip_info(session: ClientSession, request: AsyncRequest) -> Dict[str, str]:
    """"""
    response = await request.accept_json(session)

    if "error" in response:
        return {}

    return extract_keys(response, IP_INFO_RESPONSE_KEYS)


def process_ip_info_wrapper(database: Database):
    async def process_ip_info(session: ClientSession, request: AsyncRequest) -> None:
        """ """
        ip_address: str = extract_ip(request)

        if database.key_expired(ip_address, IP_DB_EXPIRE_TIME):
            ip_info: Dict[str, str] = await get_ip_info(session, request)
            database.store_entry(ip_address, ip_info)

    return process_ip_info


def ip_info():
    with Database(IP_DB_PATH) as db:

        """
        with open("ip_addresses.txt", "w") as f:
            for j1 in range(1, 2):  # 224
                for j2 in range(256):
                    for j3 in range(256):
                        for j4 in range(256):
                            f.write(f"{j1}.{j2}.{j3}.{j4}\n")
        """
        base_url = "https://ipinfo.io"

        with open("ip_addresses.txt", "r", encoding="utf-8") as file:
            ip_info_requests = []
            ip_info_process_funcs = []
            for line in islice(file, 0, 5):

                line = line.strip("\n")
                ip_info_requests.append(AsyncRequest("GET", f"/{line}"))
                ip_info_process_funcs.append(process_ip_info_wrapper(db))

            run_async_requests(ip_info_requests, ip_info_process_funcs, base_url, 1000)


if __name__ == "__main__":
    # ip_info()
    import diskcache

    db = diskcache.Cache(IP_DB_PATH)
    for ip in db:
        print(ip, db.get(ip))
