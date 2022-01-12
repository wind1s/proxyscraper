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
from ipinfo import IP_DB_PATH, process_ip_info_wrapper
from json import loads
from aiohttp import ClientSession
from asynchttprequest import AsyncRequest, run_async_requests, ProcessRequest
from database import Database
from curlget import curl_get_json
from utility import try_get_key, extract_keys

PROXY_DB_NAME = "proxies.db"
PROXY_DB_PATH = f"{PROXY_DB_NAME}"
PROXY_DB_EXPIRE_TIME = timedelta(hours=2)
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


def forge_complete_proxy_data(ip_info: dict[str, str], proxylist: dict[str, str]) -> dict[str, Any]:
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


def process_proxy_data_wrapper(proxy_db: Database, ip_db: Database) -> ProcessRequest:
    process_ip_info = process_ip_info_wrapper(ip_db)

    async def process_proxy_data(session: ClientSession, proxy_data: dict[str, str]) -> None:
        """
        Retrieves and stores a proxies data.
        """
        ip_address = proxy_data["ip"]
        await process_ip_info(session, ip_address)

        if proxy_db.key_expired(ip_address, PROXY_DB_EXPIRE_TIME):
            ip_info = ip_db.get(ip_address)
            db_entry = forge_complete_proxy_data(ip_info, proxy_data)
            proxy_db.store_entry(ip_address, db_entry)

    return process_proxy_data


def get_proxylist(page_limit: int) -> Iterable[dict[str, str]]:
    """
    Asynchronosly requests the list of proxies.
    """
    base_url = "https://proxylist.geonode.com"
    ref_template = f"/api/proxy-list?limit={0}&page={1}"
    request_ref_template = ref_template.format(page_limit)

    # Get the range of page numbers to use for requesting all proxies
    # currently available from the api.
    proxy_count = curl_get_json(base_url + ref_template.format(1, 1))["total"]
    request_count = ceil(proxy_count / page_limit)
    page_numbers = range(1, request_count + 1)

    responses = []

    async def proxylist_request(session: ClientSession, page_number: int):
        request = AsyncRequest(
            "GET", request_ref_template.format(page_number), headers={"Accept": "application/json"}
        )
        responses.append(loads(await request.send(session)))

    run_async_requests(page_numbers, proxylist_request, base_url)

    # Each request contains a data key which holds the proxy list.
    return (data for response in responses for data in response["data"])


def proxy_scraper():
    with Database(PROXY_DB_PATH) as proxy_db, Database(IP_DB_PATH) as ip_db:
        proxylist = get_proxylist(100)
        run_async_requests(proxylist, process_proxy_data_wrapper(proxy_db, ip_db))


if __name__ == "__main__":
    # proxy_scraper()

    import diskcache

    db = diskcache.Cache(PROXY_DB_PATH)

    for ip in db:
        print(ip, db.get(ip)["hostname"])
    print(len(db))
