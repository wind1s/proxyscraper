#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import argv, stderr
from datetime import timedelta
from logging import DEBUG, INFO
from ipinfo import ip_info
from proxyscraper import proxy_scraper
from requestlogging import init_logger
from database import Database
from config import (
    DEFAULT_OUTFILE,
    IP_DB_PATH,
    IP_DB_EXPIRE_TIME,
    PROXY_DB_PATH,
    PROXY_DB_EXPIRE_TIME,
)


"""
Features.

Output data to sqlite database (currently only format that works), csv, json, xml.
Command line arg what file to save to. Specify file type otherwise interpret from file extension. 
Command line arg input file for ip addresses. File types: txt, csv, stdin.
Parse urls or files for ip addresses or perform reverse dns lookup on new urls found. Parse these ip addresses.

https://realpython.com/async-io-python/#the-10000-foot-view-of-async-io
"""


def init_args():
    parser = ArgumentParser(
        "IP OSINT", description="Gather ip addresses intelligence on a large scale."
    )

    parser.add_argument(
        "input",
        nargs=1,
        type=str,
        help="Input file path.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=str,
        default=DEFAULT_OUTFILE,
        help=f"Output file path (default {DEFAULT_OUTFILE}).",
    )
    parser.add_argument(
        "--update-cache",
        dest="update_cache",
        action="store_true",
        help="Set cache mode.",
    )

    def check_positive(value):
        ivalue = int(value)

        if ivalue <= 0:
            parser.error(f"{value} is an invalid positive int value")

        return ivalue

    parser.add_argument(
        "--batch-size",
        dest="batch_size",
        type=check_positive,
        default=100,
        help="Max number of requests to run asynchronous (default 100, more than 1000 is not recommended).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Output more detailed information.",
    )

    args = parser.parse_args(argv[1:])

    return args


def main(args):
    # Switch to INFO to remove debug messages.
    init_logger(DEBUG, stderr)
    expire_time = IP_DB_EXPIRE_TIME

    if args.update_cache:
        expire_time = timedelta(0)

    with Database(IP_DB_PATH) as ip_database, Database(PROXY_DB_PATH) as proxy_database:
        proxy_scraper(
            proxy_database, ip_database, PROXY_DB_EXPIRE_TIME, IP_DB_EXPIRE_TIME, args.batch_size
        )
        """
        ip_info(args.input, ip_database, expire_time, args.batch_size)
        print(ip_database.get(args.input[0]))
        """


main(init_args())
"""
async def write_json(json_stream: IO, json_data):
    await json_stream.write(json.dumps(json_data))

"""
