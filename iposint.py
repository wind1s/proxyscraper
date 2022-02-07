#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import argv
from datetime import timedelta
from ipinfo import ip_info
from database import Database
from utility import (
    DEFAULT_OUTFILE,
    IP_DB_PATH,
    IP_DB_EXPIRE_TIME,
)


"""
Features.

Output data to sqlite database (currently only format that works), csv, json, xml.
Command line arg what file to save to. Specify file type otherwise interpret from file extension. 
Command line arg input file for ip addresses. File types: txt, csv, stdin.
Parse urls or files for ip addresses or perform reverse dns lookup on new urls found. Parse these ip addresses.

https://realpython.com/async-io-python/#the-10000-foot-view-of-async-io

url regex
(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)
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
    expire_time = IP_DB_EXPIRE_TIME

    if args.update_cache:
        expire_time = timedelta(0)

    with Database(IP_DB_PATH) as ip_database:
        ip_info(args.input, ip_database, expire_time)
        print(ip_database.get("234.54.23.2"))


main(init_args())
"""
async def write_json(json_stream: IO, json_data):
    await json_stream.write(json.dumps(json_data))

"""
