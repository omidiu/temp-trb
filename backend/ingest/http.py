"""Polite HTTP: one shared client, a fixed delay between requests, no login."""

import time

import httpx
from django.conf import settings

_client = None
_last = 0.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.5",
}


def client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True)
    return _client


def _wait():
    global _last
    delay = settings.CRAWL_DELAY - (time.monotonic() - _last)
    if delay > 0:
        time.sleep(delay)
    _last = time.monotonic()


RETRIES = 3


def _send(method: str, url: str, **kw) -> httpx.Response:
    """Retry network errors with a growing pause; after RETRIES failures, raise httpx.TransportError."""
    for attempt in range(RETRIES + 1):
        _wait()
        try:
            return client().request(method, url, **kw)
        except httpx.TransportError:
            if attempt == RETRIES:
                raise
            time.sleep(10 * (attempt + 1))


def get(url: str, **kw) -> httpx.Response:
    return _send("GET", url, **kw)


def post(url: str, **kw) -> httpx.Response:
    return _send("POST", url, **kw)
