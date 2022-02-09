"""
Provides utility function for database and ip address.
"""
from math import comb
from typing import Dict, Any, Iterable
from ipaddress import ip_address, IPv4Address, IPv6Address


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


def str_join(*strings, sep=""):
    return sep.join(strings)


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
