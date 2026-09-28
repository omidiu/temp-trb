"""Decode Nuxt's `__NUXT_DATA__` payload (the `devalue` format) into plain Python."""

import json
import re

_TAGS_WRAPPING_ONE = {"Reactive", "ShallowReactive", "Ref", "ShallowRef", "EmptyRef", "EmptyShallowRef"}


def extract(html: str):
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    return decode(json.loads(m.group(1)))


def decode(table: list):
    memo: dict[int, object] = {}

    def ref(i):
        if not isinstance(i, int) or i < 0:
            return None  # -1 undefined, -2 null, etc.
        if i in memo:
            return memo[i]
        x = table[i]
        if isinstance(x, list):
            if x and isinstance(x[0], str):
                tag = x[0]
                if tag in _TAGS_WRAPPING_ONE:
                    out = ref(x[1]) if len(x) > 1 else None
                elif tag == "Set":
                    out = [ref(j) for j in x[1:]]
                elif tag == "Map":
                    out = {ref(x[j]): ref(x[j + 1]) for j in range(1, len(x), 2)}
                elif tag in ("Date", "BigInt", "RegExp"):
                    out = x[1]
                elif tag == "null":
                    out = {ref(x[j]): ref(x[j + 1]) for j in range(1, len(x), 2)}
                else:
                    out = None
                memo[i] = out
                return out
            out = []
            memo[i] = out
            out.extend(ref(j) for j in x)
            return out
        if isinstance(x, dict):
            out = {}
            memo[i] = out
            for k, v in x.items():
                out[k] = ref(v)
            return out
        memo[i] = x
        return x

    return ref(0)
