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
from json import loads
from datetime import timedelta
from aiohttp import ClientSession
from asynchttprequest import AsyncRequest, run_async_requests, ParseRequest
from database import Database
from requestlogging import get_default_logger, log_request
from utility import extract_keys, str_join

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


async def fetch_ip_info(session: ClientSession, ip_address: str) -> dict[str, str]:
    """
    Async fetch ip address data from ipinfo.io. Logs errors to logger.
    """
    log = get_default_logger()
    base_url = "https://ipinfo.io/"
    request = AsyncRequest(
        "GET", str_join(base_url, ip_address), headers={"Accept": "application/json"}
    )

    response = await log_request(request, session)

    if response is None:
        return {}

    resp_json = loads(response)

    if "error" in resp_json:
        log.error("Response contained error %s", resp_json["error"])
        return {}

    if "bogon" in resp_json:
        log.info("Bogon ip address, discarding response")
        return {}

    log.debug("Fetched ip info of ip address %s", ip_address)
    return extract_keys(resp_json, IP_INFO_RESPONSE_KEYS)


def create_ip_info_parser(ip_database: Database, expire_time: timedelta) -> ParseRequest:
    async def parse_ip_info(session: ClientSession, ip_address: str) -> None:
        if ip_database.key_expired(ip_address, expire_time):
            ip_info = await fetch_ip_info(session, ip_address)

            if ip_info:
                ip_database.store_entry(ip_address, ip_info)

    return parse_ip_info


def ip_info(
    ip_addresses: Iterable[str], ip_database: Database, expire_time: timedelta, limit: int
) -> None:
    run_async_requests(
        ip_addresses,
        create_ip_info_parser(ip_database, expire_time),
        limit=limit,
    )
