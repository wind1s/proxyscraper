"""
Provides utility function for database and ip address.
"""
from math import comb
from typing import Dict, Any, Iterable
from re import compile as re_compile
from functools import lru_cache
from ipaddress import ip_address, IPv4Address, IPv6Address

DEFAULT_OUTFILE = "iposint.json"
UPDATE_CACHE_MODE = "update"
NO_CACHE_MODE = "none"
CACHE_MODES = (NO_CACHE_MODE, UPDATE_CACHE_MODE)
LRU_CACHE_SIZE = 128


# Regex to match URLs.
URL_RE = re_compile(
    r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
)


@lru_cache(maxsize=LRU_CACHE_SIZE)
def is_url(string: str) -> bool:
    """
    Validates a string for URL.
    """
    return bool(URL_RE.match(string))


@lru_cache(maxsize=LRU_CACHE_SIZE)
def is_ipv4(string: str) -> bool:
    """
    Validates a string for IPv4.
    """
    try:
        result = ip_address(string)
    except ValueError:
        return False

    return isinstance(result, IPv4Address)


@lru_cache(maxsize=LRU_CACHE_SIZE)
def is_ipv6(string: str) -> bool:
    """
    Validates a string for IPv6.
    """
    try:
        result = ip_address(string)
    except ValueError:
        return False

    return isinstance(result, IPv6Address)


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


def confidence(sample_size: int, reliability: float, lower: int, upper: int) -> float:
    """
    Calculates the Cumulative Binomial Distribution, interprets as a confidence value for a sample in a range.
    sample_size >= upper
    """
    score = 0
    for k in range(lower, upper):
        score += (
            comb(sample_size, k) * ((1 - reliability) ** k) * (reliability ** (sample_size - k))
        )

    return score


"""
up_time_try_count = 11
up_time = 10 / up_time_try_count
fail = 0.05  # Maximum allowed failed upTime count
# Reliability in percent, up time percentage.
R = up_time
N = up_time_try_count  # sample size

print(float(confidence(N, R, 0, int(up_time_try_count * fail))))
"""
