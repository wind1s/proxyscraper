"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause
"""
from datetime import timedelta
from os.path import abspath

# TODO: Move config data to a json file and init global variables from that file.
# Rename this file to something like "configinit" or "readconfig".

IP_DB_NAME = "ip.db"
IP_DB_PATH = abspath(f"{IP_DB_NAME}")
IP_DB_EXPIRE_TIME = timedelta(days=7)

PROXY_DB_NAME = "proxies.db"
PROXY_DB_PATH = abspath(f"{PROXY_DB_NAME}")
PROXY_DB_EXPIRE_TIME = timedelta(hours=2)

DEFAULT_OUTFILE = "iposint.json"
DEFAULT_LOG_FILE = "iposint"
