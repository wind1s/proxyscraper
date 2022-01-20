#!/usr/bin/env python3

from argparse import ArgumentParser


"""
Features.

Output data to sqlite database (currently only format that works), csv, json, xml.
Command line arg what file to save to. Specify file type otherwise interpret from file extension. 
Command line arg input file for ip addresses. File types: txt, csv, json, xml.
Choose to compress output.

"""

parser = ArgumentParser("IP address Open Source Intelligence")

parser.add_argument(
    "-o",
    "--outtype",
    dest="outtype",
    default="csv",
    choices=("csv", "json", "xml", "sqlite"),
    help="File output type",
)
parser.add_argument(
    "-i",
    "--intype",
    dest="intype",
    default="txt",
    choices=("txt", "csv", "stdin"),
    help="File input type",
)
parser.add_argument(
    "-z",
    "--compress",
    dest="compress",
    action="store_true",
    help="Compress the output",
)
