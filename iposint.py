#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import argv, exit as sys_exit
from utility import DEFAULT_OUTFILE, CACHE_MODES, NO_CACHE_MODE

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


parser = ArgumentParser("IP OSINT", description="Gathers ")

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
    "--cache-mode",
    dest="cache_mode",
    choices=CACHE_MODES,
    help="Set cache mode.",
)
parser.add_argument(
    "--no-output", dest="no_output", action="store_true", help="Do not output any results."
)
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true", help="Output more detailed information."
)

# "../test1.txt", "../test2.txt"
# args = parser.parse_args([])
args = parser.parse_args(argv)

if args.no_output and args.cache_mode == NO_CACHE_MODE:
    parser.error("--no_output and --cache_mode=none can't be set simultaneously")
    sys_exit()
