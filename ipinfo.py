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
from aiohttp import ClientSession
from asynchttprequest import run_async_requests, async_json_request
from utility import extract_keys, extract_ip
from database import Database
from request import Request

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


async def get_ip_info(request_data: Request, session: ClientSession) -> Dict[str, str]:
    """"""
    response = await async_json_request(request_data, session)

    if "error" in response:
        return {}

    return extract_keys(response, IP_INFO_RESPONSE_KEYS)


def process_ip_info_wrapper(database: Database) -> Callable[Request, ClientSession]:
    """"""

    async def process_ip_info(request_data: Request, session: ClientSession) -> None:
        """ """
        ip_address: str = extract_ip(request_data)

        if database.key_expired(ip_address, IP_DB_EXPIRE_TIME):
            ip_info: Dict[str, str] = await get_ip_info(request_data, session)
            database.store_entry(ip_address, ip_info)

    return process_ip_info


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

    with open("ip_addresses.txt", "r", encoding="utf-8") as f:
        ip_info_requests = []
        for i, line in enumerate(f):
            if i == 5:
                break

            line = line.strip("\n")
            ip_info_requests.append(Request("GET", f"/{line}"))

        run_async_requests(ip_info_requests, process_ip_info_wrapper(db), base_url, 1000)
