#!/usr/bin/env python3
"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause
"""
from typing import Any
from argparse import ArgumentParser
from sys import argv, stderr
from json import dump
from datetime import timedelta
from logging import DEBUG, INFO, WARNING
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
    parser = ArgumentParser("Proxy Scraper", description="Scrapes proxies asynchronously")

    def integer_in_range(lower_bound: int, upper_bound: int):
        def check_value(value: Any):
            ivalue = int(value)

            if ivalue > upper_bound or ivalue < lower_bound:
                parser.error(f"{value} is invalid, must be {lower_bound} <= value <= {upper_bound}")

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
        ("--ip-update",): {
            "dest": "ip_update",
            "action": "store_true",
            "help": "Update the ip address info cache",
        },
        ("--batch-size",): {
            "dest": "batch_size",
            "type": integer_in_range(1, 10000),
            "default": 500,
            "help": "Max number of requests to run asynchronous (default 100, more than 1000 is not recommended).",
        },
        ("--google",): {
            "dest": "google",
            "action": "store_true",
            "help": "Filter after google accepted proxies.",
        },
        # All anonymity levels above the specifed is also accepted.
        ("--anon",): {
            "dest": "anonymity",
            "choices": ("transparent", "anonymous", "elite"),
            "default": "anonymous",
            "help": "Specify a minimum proxy anonymity level (default anonymous)",
        },
        ("--speed",): {
            "dest": "speed",
            "type": integer_in_range(1, 1000),
            "default": 1000,
            "help": "Specify maximal response time (ms) of proxy server ",
        },
        # Can specify multiple protocols.
        ("--protocols",): {
            "dest": "protocols",
            "nargs": "*",
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
            "help": "Output more detailed information (-vv for even more verbose).",
        },
    }

    for arg, settings in argument_definitions.items():
        parser.add_argument(*arg, **settings)

    return parser.parse_args(raw_args)


def get_verbosity(verbose_count: int) -> int:
    if verbose_count in (None, 0):
        return WARNING

    if verbose_count == 1:
        return INFO

    return DEBUG


def main(args):
    # Switch to INFO to remove debug messages.

    init_logger(get_verbosity(args.verbose), stderr)
    proxy_db_expire_time = PROXY_DB_EXPIRE_TIME
    ip_db_expire_time = IP_DB_EXPIRE_TIME

    with Database(IP_DB_PATH) as ip_database, Database(PROXY_DB_PATH) as proxy_database:
        if args.update or args.only_update:
            if args.ip_update:
                ip_db_expire_time = timedelta(0)

            proxy_db_expire_time = timedelta(0)
            proxy_scraper(
                proxy_database,
                ip_database,
                proxy_db_expire_time,
                ip_db_expire_time,
                args.batch_size,
            )

        if not args.only_update:
            with open(args.output, "w", encoding="utf-8") as json_file:
                entries = proxy_database.get_entries()
                json_data = {}

                for entry in entries:
                    proxy_data = proxy_database.get(entry)

                    # If google accepted proxy is specified and the proxy is not google accepted.
                    if args.google and not proxy_data["google"]:
                        continue

                    # If the proxy does not have common protocols with the specified ones.
                    if args.protocols is not None and not set(args.protocols).intersection(
                        set(proxy_data["protocols"])
                    ):

                        continue

                    # If the proxy is slower than the specified speed.
                    if proxy_data["speed"] > args.speed:
                        continue

                    # If anonymous anonymity was specified and proxy does not have higher or equal.
                    if (
                        args.anonymity == "anonymous"
                        and proxy_data["anonymityLevel"] == "transparent"
                    ):
                        continue

                    # If elite anonymity was specified and proxy does not have higher or equal.
                    if args.anonymity == "elite" and proxy_data["anonymityLevel"] in (
                        "transparent",
                        "anonymous",
                    ):
                        continue

                    json_data[entry] = proxy_data

                dump(json_data, json_file)


main(init_args(argv[1:]))
