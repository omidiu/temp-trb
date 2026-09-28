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


def get(url: str, **kw) -> httpx.Response:
    _wait()
    return client().get(url, **kw)


def post(url: str, **kw) -> httpx.Response:
    _wait()
    return client().post(url, **kw)
