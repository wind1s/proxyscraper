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
from typing import Iterable
from sys import stderr
from json import loads
from datetime import timedelta
from logging import Logger
from aiohttp import ClientSession
from asynchttprequest import AsyncRequest, run_async_requests
from utility import extract_keys, IP_INFO_LOG
from database import Database
from requestlogging import log_request, init_logger

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


async def fetch_ip_info(session: ClientSession, ip_address: str, logger: Logger) -> dict[str, str]:
    base_url = "https://ipinfo.io"
    request = AsyncRequest(
        "GET", "/".join((base_url, ip_address)), headers={"Accept": "application/json"}
    )

    response = loads(await log_request(request, session, logger))

    if response is None or "error" in response or response["bogon"]:
        return {}

    return extract_keys(response, IP_INFO_RESPONSE_KEYS)


def parse_ip_info_wrapper(ip_database: Database, logger: Logger, expire_time: timedelta):
    async def parse_ip_info(session: ClientSession, ip_address: str) -> None:
        if ip_database.key_expired(ip_address, expire_time):
            ip_info = await fetch_ip_info(session, ip_address, logger)

            if ip_info:
                ip_database.store_entry(ip_address, ip_info)

    return parse_ip_info


def ip_info(
    ip_addresses: Iterable[str],
    ip_database: Database,
    expire_time: timedelta,
) -> None:
    run_async_requests(
        ip_addresses,
        parse_ip_info_wrapper(ip_database, init_logger(IP_INFO_LOG, stderr), expire_time),
    )
