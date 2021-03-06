"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause

Defines curl get wrappers.
"""
from typing import Optional
from io import BytesIO
from pycurl import Curl, CAINFO, SSL_VERIFYPEER, USERAGENT, URL, WRITEDATA, HTTPHEADER
from certifi import where
from utility import load_json


def curl_get(url, options) -> str:
    """
    Initializes a "secure" curl get request.
    """
    buffer = BytesIO()
    curl = Curl()

    curl_options = {
        URL: url,
        WRITEDATA: buffer,
        USERAGENT: "Firefox/94.0",
        CAINFO: where(),
        SSL_VERIFYPEER: 0,
        **options,
    }

    set_curl_options(curl_options, curl)
    curl.perform()
    curl.close()

    # We have to know the encoding in order to print it to a text file
    # such as standard output.
    return buffer.getvalue().decode("iso-8859-1")


def set_curl_options(options, curl) -> None:
    """
    Set options for curl object.
    """
    for option, value in options.items():
        curl.setopt(option, value)


def curl_get_json(url) -> Optional[dict]:
    """
    Performs a curl get request and returns json data as a dictionary.
    """
    options = {HTTPHEADER: ["Accept: application/json"]}
    data = curl_get(url, options)

    json_data = load_json(data)
    if json_data is str:
        return None

    return json_data


def curl_get_html(url) -> str:
    """
    Helper function to fetch html responses.
    """
    options = {HTTPHEADER: ["Accept: text/html"]}
    return curl_get(url, options)
