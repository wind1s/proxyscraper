#!/usr/local/env python3
"""
Compiles a database of proxy servers with their respective metadata.
Also adds country corruption index, server fraud score and more.

Links:
    https://geonode.com/free-proxy-list
    https://proxylist.geonode.com/api/proxy-list?limit=1000&page=1

Custom proxy key value pair:
    key = ip (123.123.123.123)
    value = (this dict)
    {
        "port":
        "anonymityLevel":
        "protocols": [list of supported protocols]
        "google": (true or false if google approved proxy)
        "org": [list of all orgs and asn]
        "latency":
        "responseTime":
        "upTime":
        "upTimeTryCount":
        "created_at":
        "updated_at":
        "hostname":
        "city":
        "region":
        "postal":
        "country":
        "timezone":
        "loc":
        "corruptionindex":
        "entry_time":
    }
"""

from typing import Iterable, Any
from math import ceil
from datetime import timedelta
from json import loads
from ipinfo import create_ip_info_parser
from aiohttp import ClientSession
from asynchttprequest import AsyncRequest, run_async_requests, ParseRequest
from database import Database
from curlget import curl_get_json
from requestlogging import log_request, get_default_logger, log_db_entry_status
from utility import try_get_key, extract_keys, str_join
from config import IP_DB_NAME, PROXY_DB_NAME


PROXYLIST_RESPONSE_KEYS = (
    "port",
    "anonymityLevel",
    "protocols",
    "google",
    "org",
    "latency",
    "responseTime",
    "upTime",
    "upTimeTryCount",
    "created_at",
    "updated_at",
)


def forge_proxy_entry(ip_info: dict[str, str], proxylist: dict[str, str]) -> dict[str, Any]:
    """
    Creates the custom database entry for a proxies data.
    """
    db_entry = {**extract_keys(proxylist, PROXYLIST_RESPONSE_KEYS), **ip_info}
    db_entry["org"] = ";".join(
        origin
        for origin in (
            try_get_key("org", ip_info),
            try_get_key("asn", proxylist),
            try_get_key("org", proxylist),
        )
        if origin is not None
    )

    db_entry["created_at"].replace("T", " ").replace("Z", "")
    db_entry["updated_at"].replace("T", " ").replace("Z", "")
    # db_entry["corruptionindex"] = get_corruption_index(ip_info["country"])

    return db_entry


def create_proxy_data_parser(
    proxy_db: Database, ip_db: Database, proxy_expire_time: timedelta, ip_expire_time: timedelta
) -> ParseRequest:
    parse_ip_info = create_ip_info_parser(ip_db, ip_expire_time)

    async def parse_proxy_data(session: ClientSession, proxy_data: dict[str, str]) -> None:
        """
        Retrieves and stores a proxies data, including it's ip address data separetly.
        """
        ip_address = proxy_data["ip"]
        await parse_ip_info(session, ip_address)

        if proxy_db.key_expired(ip_address, proxy_expire_time):
            ip_info = ip_db.get(ip_address)
            db_entry = forge_proxy_entry(ip_info, proxy_data)
            proxy_db.store_entry(ip_address, db_entry)

    return parse_proxy_data


def fetch_proxylist(page_limit: int, request_limit: int) -> Iterable[dict[str, str]]:
    """
    Asynchronosly requests a list of proxies from proxylist.geonode.com.
    """
    base_url = "https://proxylist.geonode.com"
    api_ref_template = "/api/proxy-list?limit={}&page={{}}"
    proxylist_api_template = api_ref_template.format(page_limit)
    single_proxy_query_url = str_join(base_url, api_ref_template.format(1, 1))

    log = get_default_logger()
    request = AsyncRequest("GET", "", headers={"Accept": "application/json"})
    responses = []

    def fetch_page_range():
        # Get the range of page numbers to use for requesting all proxies
        # currently available from the api.
        response = curl_get_json(single_proxy_query_url)

        if response is None:
            log.error("Could not fetch proxy count from %s", single_proxy_query_url)
            return range(0)

        proxy_count = response["total"]
        request_count = ceil(proxy_count / page_limit)
        return range(1, request_count + 1)

    async def proxylist_request(session: ClientSession, page_number: int):
        request.url = proxylist_api_template.format(page_number)
        resp = await log_request(request, session)

        # If response is none, an error occurred and the fetch could not be made.
        if resp is None:
            log.warning("Could not fetch proxylist from %s", request.url)
            return

        # Response contains a key data with all the proxies data.
        proxylist_data = loads(resp)["data"]
        log.info("Fetched %d proxies from page %d", len(proxylist_data), page_number)
        responses.append(proxylist_data)

    run_async_requests(
        fetch_page_range(), proxylist_request, base_url=base_url, limit=request_limit
    )

    # Each request contains a data key which holds the proxy list.
    return (proxy_data for proxylist in responses for proxy_data in proxylist)


def proxy_scraper(
    proxy_db: Database,
    ip_db: Database,
    proxy_expire_time: timedelta,
    ip_expire_time: timedelta,
    limit: int,
):

    proxylist = fetch_proxylist(100, limit)

    prev_proxy_db_count = proxy_db.get_count()
    prev_ip_db_count = ip_db.get_count()

    run_async_requests(
        proxylist,
        create_proxy_data_parser(proxy_db, ip_db, proxy_expire_time, ip_expire_time),
        limit=limit,
    )

    new_proxies_count = proxy_db.get_count() - prev_proxy_db_count
    new_ips_count = ip_db.get_count() - prev_ip_db_count
    log_db_entry_status(new_proxies_count, PROXY_DB_NAME)
    log_db_entry_status(new_ips_count, IP_DB_NAME)
