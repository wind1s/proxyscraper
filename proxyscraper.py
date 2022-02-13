#!/usr/bin/env python3

from typing import Any
from argparse import ArgumentParser
from sys import argv, stderr
from datetime import timedelta
from logging import DEBUG, INFO
from scraper import proxy_scraper
from requestlogging import init_logger
from database import Database
from config import (
    DEFAULT_OUTFILE,
    IP_DB_PATH,
    IP_DB_EXPIRE_TIME,
    PROXY_DB_PATH,
    PROXY_DB_EXPIRE_TIME,
)


def init_args(raw_args):
    parser = ArgumentParser("Proxy Scraper", description="Scrapes proxies")

    def integer_in_range(lower_bound: int, upper_bound: int):
        def check_value(value: Any):
            ivalue = int(value)

            if ivalue > upper_bound or ivalue < lower_bound:
                parser.error(f"{value} is invalid, must be {lower_bound} <= value <= {upper_limit}")

            return ivalue

        return check_value

    # Add functionality to extract proxies, filter after google accepted, fail rate, maximum response time and anonymity level.

    argument_definitions = {
        ("output",): {
            "nargs": "?",
            "type": str,
            "default": DEFAULT_OUTFILE,
            "help": f"Output file path (default {DEFAULT_OUTFILE}).",
        },
        ("-u", "--update"): {
            "dest": "update",
            "action": "store_true",
            "help": "Updates the cache by scraping for more proxies.",
        },
        ("--only-update",): {
            "dest": "only_update",
            "action": "store_true",
            "help": "Only update the cache and do not output a file with proxies.",
        },
        ("--batch-size",): {
            "dest": "batch_size",
            "type": integer_in_range(1, 10000),
            "default": 200,
            "help": "Max number of requests to run asynchronous (default 100, more than 1000 is not recommended).",
        },
        ("--google",): {
            "dest": "google",
            "action": "store_true",
            "help": "Filter after google accepted proxies.",
        },
        ("--fail",): {
            "dest": "fail_rate",
            "type": integer_in_range(0, 100),
            "help": "Filter after maximum fail rate (%) of proxy connection tries.",
        },
        # All anonymity levels above the specifed is also accepted.
        ("--anon"): {
            "dest": "anonymity",
            "choices": ("transparent", "anonymous", "elite"),
            "default": "anonymous",
            "help": "Specify a minimum proxy anonymity level (default anonymous)",
        },
        # Some have none as response time, include them in the result but put them at the bottom.
        ("--response-time"): {
            "dest": "resp_time",
            "type": integer_in_range(1, 1000),
            "help": "Specify maximal response time (ms) of proxy server ",
        },
        # Can specify multiple protocols.
        ("--protocol",): {
            "dest": "protocol",
            "nargs": "?",
            "choices": ("http", "https", "socks4", "socks5"),
            "default": None,
            "action": "extend",
            "help": "Specify what protocol(s) the proxy should have",
        },
        # Counts the amount of v specified.
        # 1 v means that INFO messages will be logged, 2 v means also DEBUG messages will be logged.
        ("-v", "--verbose"): {
            "dest": "verbose",
            "action": "count",
            "help": "Output more detailed information.",
        },
    }

    for arg, settings in argument_definitions.items():
        parser.add_argument(*arg, **settings)

    return parser.parse_args(raw_args)


def main(args):
    # Switch to INFO to remove debug messages.
    init_logger(DEBUG, stderr)
    expire_time = PROXY_DB_EXPIRE_TIME

    if args.update_cache:
        expire_time = timedelta(0)

    with Database(IP_DB_PATH) as ip_database, Database(PROXY_DB_PATH) as proxy_database:
        proxy_scraper(proxy_database, ip_database, expire_time, IP_DB_EXPIRE_TIME, args.batch_size)
        """
        ip_info(args.input, ip_database, expire_time, args.batch_size)
        print(ip_database.get(args.input[0]))
        """


main(init_args(argv[1:]))
