"""
Provides utility function for database and ip address.
"""
from math import comb
from typing import Dict, Any, Iterator
from request import Request


def extract_ip(request: Request) -> str:
    """
    Extracts the ip address from a url reference in a request obj.
    """
    return request.url[1:]


def extract_keys(dct: Dict[Any, Any], keys: Iterator[Any]) -> Dict[Any, Any]:
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
