# JOK++
from typing import Optional
from urllib.parse import quote_plus


def hostPortToString(host: str, port: int) -> str:
    return "[{:s}]:{:d}".format(host, port)


def encodeUrlString(source: str) -> Optional[str]:
    try:
        return quote_plus(
            str(source),
            encoding="utf-8",
            errors="strict")
    except UnicodeError:
        return None


def urlJoin(base: str, *args: str) -> str:
    result = base.rstrip("/")
    for item in args:
        item = item.strip("/")
        if item:
            result += "/" + item
    return result
