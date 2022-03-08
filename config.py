"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause
"""
import sys
from typing import Any
from datetime import timedelta
from os.path import abspath
from argparse import ArgumentParser
from utility import load_json


IP_DB_NAME = ""
IP_DB_PATH = ""
IP_DB_EXPIRE_TIME = ""

PROXY_DB_NAME = ""
PROXY_DB_PATH = ""
PROXY_DB_EXPIRE_TIME = ""

DEFAULT_OUTFILE = ""
DEFAULT_LOGGER = ""

CONFIG_FILE_NAME = "config.json"


def err_print(string: str):
    print(string, file=sys.stderr)
    sys.exit(1)


def get_setting(config_data: dict, setting: str) -> Any:
    if setting not in config_data:
        err_print(f"Missing config setting: {setting} in {CONFIG_FILE_NAME}")

    return config_data[setting]


def init_config_vars():
    with open(CONFIG_FILE_NAME, "r", encoding="utf-8") as config_json:
        config_data = load_json(config_json)
        if isinstance(config_data, Exception):
            err_print(f"Could not load {CONFIG_FILE_NAME}\n{config_data}")

    # pylint: disable=global-statement
    global IP_DB_NAME, IP_DB_PATH, IP_DB_EXPIRE_TIME
    global PROXY_DB_NAME, PROXY_DB_PATH, PROXY_DB_EXPIRE_TIME
    global DEFAULT_LOGGER, DEFAULT_OUTFILE

    IP_DB_NAME = get_setting(config_data, "ip_db_name")
    IP_DB_PATH = abspath(f"{IP_DB_NAME}")
    IP_DB_EXPIRE_TIME = timedelta(**get_setting(config_data, "ip_db_expire_time"))

    PROXY_DB_NAME = get_setting(config_data, "proxy_db_name")
    PROXY_DB_PATH = abspath(f"{PROXY_DB_NAME}")
    PROXY_DB_EXPIRE_TIME = timedelta(**get_setting(config_data, "proxy_db_expire_time"))

    DEFAULT_OUTFILE = get_setting(config_data, "default_outfile_name")
    DEFAULT_LOGGER = get_setting(config_data, "default_logger_name")


init_config_vars()
