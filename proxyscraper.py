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

from math import ceil
from typing import Iterator, Dict, Any, Callable, Tuple
from datetime import timedelta
from aiohttp import ClientSession
from asynchttprequest import run_async_requests, async_json_request
from request import Request
from database import Database
from curlget import curl_get_json
from ipinfo import IP_DB_EXPIRE_TIME, get_ip_info, IP_DB_PATH
from utility import try_get_key, extract_keys, extract_ip

PROXY_DB_NAME = "proxies.db"
PROXY_DB_PATH = f"{PROXY_DB_NAME}"
PROXY_DB_EXPIRE_TIME = timedelta(hours=2).total_seconds()
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


def proxy_db_entry(ip_info: Dict[str, str], proxylist: Dict[str, str]) -> Dict[str, Any]:
    """
    Creates the custom database entry for a proxies data.
    """
    db_entry = {**extract_keys(proxylist, PROXYLIST_RESPONSE_KEYS), **ip_info}
    db_entry["org"] = [
        origin
        for origin in (
            try_get_key("org", ip_info),
            try_get_key("org", proxylist),
            try_get_key("asn", proxylist),
        )
        if origin is not None
    ]

    db_entry["created_at"].replace("T", " ").replace("Z", "")
    db_entry["updated_at"].replace("T", " ").replace("Z", "")
    # db_entry["corruptionindex"] = get_corruption_index(ip_info["country"])

    return db_entry


def init_requests(page_limit: int, base_url: str, url_ref: str) -> Iterator[Request]:
    """
    Creates the request arguments to get all proxies currently listed.
    Amount of requests is based on the limit of proxies each request should take.
    """
    proxy_count = curl_get_json(base_url + url_ref.format(1, 1))["total"]
    request_count = ceil(proxy_count / page_limit)

    return (Request("GET", url_ref.format(page_limit, i)) for i in range(1, request_count + 1))


def process_proxy_data_wrapper(
    proxylist: Tuple[Dict[str, str]], proxy_db: Database, ip_db: Database
) -> Callable[Request, ClientSession]:
    """"""
    call_count = 0

    async def process_proxy_data(request: Request, session: ClientSession) -> None:
        """
        Retrieves and stores a proxies data.
        """
        nonlocal call_count
        ip_address = extract_ip(request)

        if ip_db.key_expired(ip_address, IP_DB_EXPIRE_TIME):
            ip_info = await get_ip_info(request, session)

            if not ip_info:
                return

            ip_db.store_entry(ip_address, ip_info)

        if proxy_db.key_expired(ip_address, PROXY_DB_EXPIRE_TIME):
            ip_info = ip_db.get(ip_address)
            db_entry = proxy_db_entry(ip_info, proxylist[call_count])
            proxy_db.store_entry(ip_address, db_entry)

        call_count += 1

    return process_proxy_data


def get_proxylist(page_limit: int) -> Iterator[Dict[str, str]]:
    """
    Asynchronosly requests the list of proxies.
    """
    base_url = "https://proxylist.geonode.com"
    url_ref = "/api/proxy-list?limit={0}&page={1}"

    responses = []
    requests_data = init_requests(page_limit, base_url, url_ref)
    run_async_requests(
        requests_data, lambda d, s: responses.append(async_json_request(d, s)), base_url
    )

    # Each request contains a data key which holds the proxy list.
    return tuple(data for response in responses for data in response["data"])


if __name__ == "__main__":
    with Database(PROXY_DB_PATH) as proxy_db, Database(IP_DB_PATH) as ip_db:
        base_url = "https://ipinfo.io"

        proxylist = get_proxylist(100)
        requests_data = (Request("GET", f"/{data['ip']}") for data in proxylist)

        run_async_requests(
            requests_data, process_proxy_data_wrapper(proxylist, proxy_db, ip_db), base_url
        )
