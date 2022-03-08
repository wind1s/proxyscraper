"""
* Copyright (c) 2022, William Minidis <william.minidis@protonmail.com>
*
* SPDX-License-Identifier: BSD-2-Clause

Provides utility function for database and ip address.
"""
from typing import IO, Union
from io import TextIOBase
from math import comb
from typing import Dict, Any, Iterable
from ipaddress import ip_address, IPv4Address, IPv6Address
from json import load, loads, JSONDecodeError


def is_ipv4(string: str) -> bool:
    """
    Validates a string for IPv4.
    """
    try:
        result = ip_address(string)
    except ValueError:
        return False

    return isinstance(result, IPv4Address)


def is_ipv6(string: str) -> bool:
    """
    Validates a string for IPv6.
    """
    try:
        result = ip_address(string)
    except ValueError:
        return False

    return isinstance(result, IPv6Address)


def load_json(stream) -> Union[dict, Exception]:
    try:
        if isinstance(stream, TextIOBase):
            json_data = load(stream)
        elif isinstance(stream, str):
            json_data = loads(stream)
        else:
            raise TypeError(f"Unknown type to load json from: {stream}")

    except (JSONDecodeError, TypeError) as err:
        return err

    return json_data


def extract_keys(dct: Dict[Any, Any], keys: Iterable[Any]) -> Dict[Any, Any]:
    """
    Try to extract specific keys for a dictionary, defaulting value to None if key does not exist.
    """
    return {key: try_get_key(key, dct) for key in keys}


def try_get_key(key: Any, dct: Dict[Any, Any]) -> Any:
    """
    Tires to get a key from a dictionary, returns None if it does not exist.
    """
    if key in dct:
        return dct[key]

    return None


def str_join(*strings, sep="") -> str:
    """
    Joins multiple strings with optional separator.
    """
    return sep.join(strings)


def confidence(sample_size: int, reliability: float, upper: int) -> float:
    """
    Calculates the Cumulative Binomial Distribution, interprets as a confidence value for a sample in a range.
    sample_size >= upper
    """
    score = 0
    for k in range(0, upper):
        score += (
            comb(sample_size, k) * ((1 - reliability) ** k) * (reliability ** (sample_size - k))
        )

    return score


"""
up_time_try_count = 11
up_time = 10 / up_time_try_count
fail = 0.05  # Maximum allowed failed upTime count
# Reliability in percent, up time percentage.
R = 
N =   # sample size

print(float(confidence(up_time_try_count, up_time, int(up_time_try_count * fail))))
"""
