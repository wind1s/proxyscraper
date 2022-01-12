#!/usr/bin/env python3

from argparse import ArgumentParser

parser = ArgumentParser("IP address Open Source Intelligence")

"""
Features.

Output data to sqlite database (currently only format that works), csv, json, xml.
Command line arg what file to save to. Specify file type otherwise interpret from file extension. 
Command line arg input file for ip addresses. File types: txt, csv, json, xml.
Choose to compress output.

"""

parser.add_argument()
parser.add_argument()
