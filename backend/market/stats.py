"""Market statistics: fair price and verdict per Offer; Popularity and Depreciation per model.

All numbers come from the snapshot and are asking prices, not sale prices.
"""

import math
import statistics
from collections import defaultdict
from datetime import date

from django.db import transaction

from .models import ModelStats, Offer

MIN_COMPARABLES = 5
SUSPICIOUS_BELOW = 0.25   # more than 25% under fair price
GREAT_P, OVERPRICED_P = 0.8, 0.2

# (confidence, predicate(offer, candidate)) — first tier with ≥ MIN_COMPARABLES wins.
TIERS = [
    ("high", lambda o, c: c.vehicle_id == o.vehicle_id and c.body_condition == o.body_condition
        and c.year == o.year and abs(c.mileage - o.mileage) <= 20_000),
    ("medium", lambda o, c: c.vehicle_id == o.vehicle_id and abs(c.year - o.year) <= 1
        and abs(c.mileage - o.mileage) <= 40_000),
    ("low", lambda o, c: abs(c.year - o.year) <= 1 and abs(c.mileage - o.mileage) <= 40_000),  # same family
]


def solar_year(today: date | None = None) -> int:
    today = today or date.today()
    return today.year - 621 if (today.month, today.day) >= (3, 21) else today.year - 622


def drop_outliers(prices: list[int]) -> list[int]:
    if len(prices) < 4:
        return prices
    q1, _, q3 = statistics.quantiles(prices, n=4)
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return [p for p in prices if lo <= p <= hi]


def comparables(offer, pool) -> tuple[str, list]:
    """Return (confidence, comparable Offers) or ('', []) when no tier reaches MIN_COMPARABLES."""
    for confidence, same in TIERS:
        found = [c for c in pool if c.pk != offer.pk and same(offer, c)]
        kept = set(drop_outliers([c.price for c in found]))
        found = [c for c in found if c.price in kept]
        if len(found) >= MIN_COMPARABLES:
            return confidence, found
    return "", []


def verdict(price: int, comps: list) -> tuple[int, float, str]:
    """(fair price, p = share of comparables priced higher, verdict)."""
    fair = int(statistics.median(c.price for c in comps))
    p = sum(c.price > price for c in comps) / len(comps)
    if price < (1 - SUSPICIOUS_BELOW) * fair:
        v = Offer.Verdict.SUSPICIOUS
    elif p >= GREAT_P:
        v = Offer.Verdict.GREAT
    elif p <= OVERPRICED_P:
        v = Offer.Verdict.OVERPRICED
    else:
        v = Offer.Verdict.FAIR
    return fair, p, v


def depreciation(offers, this_year: int) -> float | None:
    """Average share of price lost per year: fit log(median price) against age; needs ≥ 3 years with ≥ 5 Offers."""
    by_year = defaultdict(list)
    for o in offers:
        by_year[o.year].append(o.price)
    points = [(this_year - y, math.log(statistics.median(ps))) for y, ps in by_year.items() if len(ps) >= 5]
    if len(points) < 3:
        return None
    ages, logs = zip(*points)
    mean_a, mean_l = statistics.fmean(ages), statistics.fmean(logs)
    var = sum((a - mean_a) ** 2 for a in ages)
    if var == 0:
        return None
    slope = sum((a - mean_a) * (l - mean_l) for a, l in zip(ages, logs)) / var
    return round(1 - math.exp(slope), 4)


@transaction.atomic
def compute_market() -> dict:
    offers = list(Offer.objects.select_related("vehicle"))
    eligible = [o for o in offers if not o.exclusion]
    by_family = defaultdict(list)
    for o in eligible:
        by_family[o.vehicle.family].append(o)

    stats = defaultdict(int)
    for o in offers:
        o.fair_price, o.p_cheaper, o.confidence, o.comparable_ids = None, None, "", []
        o.verdict = Offer.Verdict.UNKNOWN
        if not o.exclusion:
            confidence, comps = comparables(o, by_family[o.vehicle.family])
            if comps:
                o.fair_price, o.p_cheaper, o.verdict = verdict(o.price, comps)
                o.confidence, o.comparable_ids = confidence, [c.pk for c in comps]
        stats[o.verdict] += 1
    Offer.objects.bulk_update(offers, ["fair_price", "p_cheaper", "verdict", "confidence", "comparable_ids"])

    this_year = solar_year()
    counts = {fam: len(os) for fam, os in by_family.items()}
    ModelStats.objects.all().delete()
    n = len(counts)
    for fam, count in counts.items():
        popularity = sum(c < count for c in counts.values()) / (n - 1) if n > 1 else 1.0
        ModelStats.objects.create(model_key=fam, offer_count=count, popularity=round(popularity, 3),
                                  depreciation=depreciation(by_family[fam], this_year))
    return dict(stats)
