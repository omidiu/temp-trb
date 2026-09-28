"""Zero results → suggest loosening one Constraint at a time, with the result count each would give."""

import copy
import math

from market.models import Offer

from . import fa
from .intent import FAMILIES
from .ranking import passes

MIN_USEFUL = 5  # a budget suggestion aims for at least this many results


def _pool():
    return list(Offer.objects.select_related("vehicle").filter(exclusion=""))


def _count(pool, c):
    return sum(passes(o, c) for o in pool)


def suggestions(constraints: dict, limit: int = 4) -> list[dict]:
    pool = _pool()
    out = []

    def try_patch(label, patch):
        c = copy.deepcopy(constraints)
        c.update(patch)
        n = _count(pool, c)
        if n:
            out.append({"label": label, "patch": patch, "count": n})

    c = constraints
    if c.get("max_price") is not None:
        # Smallest budget (rounded up to 10M) that gives a handful of results under the other Constraints.
        others = dict(c, max_price=None)
        prices = sorted(o.price for o in pool if passes(o, others))
        if prices:
            target = prices[min(MIN_USEFUL, len(prices)) - 1]
            budget = int(math.ceil(target / 10_000_000) * 10_000_000)
            try_patch(f"با بودجه {fa.toman(budget)}", {"max_price": budget})
    if c.get("gearbox"):
        other = "manual" if c["gearbox"] == "automatic" else "automatic"
        try_patch("با گیربکس دستی" if other == "manual" else "با گیربکس اتوماتیک", {"gearbox": None})
    if c.get("fuel_type"):
        try_patch("بدون شرط سوخت", {"fuel_type": None})
    if c.get("body_condition") == "clean":
        try_patch("با رنگ جزئی", {"body_condition": "minor"})
    elif c.get("body_condition") == "minor":
        try_patch("بدون شرط بدنه", {"body_condition": None})
    if c.get("models"):
        try_patch("همهٔ مدل‌ها", {"models": []})
    if c.get("exclude_models"):
        names = "، ".join(FAMILIES.get(m, m) for m in c["exclude_models"])
        try_patch(f"با {names} هم", {"exclude_models": []})
    if c.get("min_year") is not None:
        try_patch(f"مدل‌های قدیمی‌تر از {fa.digits(c['min_year'])} هم", {"min_year": None})
    if c.get("max_mileage") is not None:
        try_patch("بدون سقف کارکرد", {"max_mileage": None})
    if c.get("min_price") is not None:
        try_patch("بدون کف قیمت", {"min_price": None})
    out.sort(key=lambda s: -s["count"])
    return out[:limit]
