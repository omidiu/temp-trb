"""Rank Offers against a resolved Intent. Every number here is inspectable in the UI.

total = (2·deal + Σ wᵢ·sᵢ) / (2 + Σ wᵢ),  w = 1 (normal) or 2 (strong)

- sᵢ ∈ [0, 1] is each Preference's score: a percentile within the candidate set for numeric ones
  (price, mileage, year, fuel use, airbags, Popularity, Depreciation), match/no-match otherwise.
- deal = the verdict's p (share of comparables priced higher); 0.5 without a verdict; 0 when suspicious.
  It always weighs 2: value for money matters to every buyer.
"""

import statistics
from collections import Counter

from market.models import ModelStats, Offer

DEAL_WEIGHT = 2
WEIGHTS = {"normal": 1, "strong": 2}
OVER_BUDGET = 1.10
CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1, "": 0}
CONDITION_ALLOWED = {"clean": {"clean"}, "minor": {"clean", "minor"}}
COND_SCORE = {"clean": 1.0, "minor": 0.5, "major": 0.0}


def total_score(deal: float, parts: list[tuple[float, float]]) -> float:
    """parts = [(weight, score)]."""
    return (DEAL_WEIGHT * deal + sum(w * s for w, s in parts)) / (DEAL_WEIGHT + sum(w for w, _ in parts))


def percentile_scores(values: list, higher_is_better: bool) -> list[float | None]:
    """Mid-rank percentile of each value among the known values; None stays None (scored neutral later)."""
    known = [v for v in values if v is not None]
    n = len(known)
    out = []
    for v in values:
        if v is None:
            out.append(None)
            continue
        if n <= 1:
            out.append(1.0)
            continue
        below = sum(k < v for k in known) if higher_is_better else sum(k > v for k in known)
        equal = sum(k == v for k in known) - 1
        out.append((below + 0.5 * equal) / (n - 1))
    return out


def passes(o: Offer, c: dict, max_price_factor: float = 1.0) -> bool:
    v = o.vehicle
    if c.get("city") and o.city != c["city"]:
        return False
    if c.get("max_price") is not None and o.price > c["max_price"] * max_price_factor:
        return False
    if c.get("min_price") is not None and o.price < c["min_price"]:
        return False
    if c.get("min_year") is not None and o.year < c["min_year"]:
        return False
    if c.get("max_year") is not None and o.year > c["max_year"]:
        return False
    if c.get("max_mileage") is not None and o.mileage > c["max_mileage"]:
        return False
    if c.get("models") and v.family not in c["models"]:
        return False
    if c.get("exclude_models") and v.family in c["exclude_models"]:
        return False
    if c.get("gearbox") and o.gearbox != c["gearbox"]:
        return False
    if c.get("fuel_type") and o.fuel_type != c["fuel_type"]:
        return False
    if c.get("body_condition") and o.body_condition not in CONDITION_ALLOWED[c["body_condition"]]:
        return False
    return True


def candidates(c: dict) -> tuple[list[Offer], list[Offer]]:
    """(within budget, up to 10% over budget). Placeholder-price Offers are never searchable."""
    pool = Offer.objects.select_related("vehicle").prefetch_related("listings").exclude(exclusion="placeholder")
    main, over = [], []
    for o in pool:
        if passes(o, c):
            main.append(o)
        elif c.get("max_price") is not None and passes(o, c, OVER_BUDGET):
            over.append(o)
    return main, over


def _like_reference(family: str) -> tuple[str, float] | None:
    offers = list(Offer.objects.filter(vehicle__family=family).select_related("vehicle"))
    if not offers:
        return None
    body = Counter(o.vehicle.body_type for o in offers).most_common(1)[0][0]
    return body, statistics.median(o.price for o in offers)


def preference_scores(prefs: list[dict], offers: list[Offer]) -> dict[str, list[float | None]]:
    stats = {m.model_key: m for m in ModelStats.objects.all()}
    col = {}
    for p in prefs:
        key = p["key"]
        if key == "cheaper":
            col[key] = percentile_scores([o.price for o in offers], higher_is_better=False)
        elif key == "newer":
            col[key] = percentile_scores([o.year for o in offers], higher_is_better=True)
        elif key == "low_mileage":
            col[key] = percentile_scores([o.mileage for o in offers], higher_is_better=False)
        elif key == "low_fuel":
            col[key] = percentile_scores([o.vehicle.fuel_consumption for o in offers], higher_is_better=False)
        elif key == "more_airbags":
            col[key] = percentile_scores([o.vehicle.airbags for o in offers], higher_is_better=True)
        elif key == "popular":
            col[key] = percentile_scores([getattr(stats.get(o.vehicle.family), "popularity", None) for o in offers], True)
        elif key == "holds_value":
            col[key] = percentile_scores([getattr(stats.get(o.vehicle.family), "depreciation", None) for o in offers], False)
        elif key == "has_abs":
            col[key] = [None if o.vehicle.abs is None else float(bool(o.vehicle.abs)) for o in offers]
        elif key == "body_sedan":
            col[key] = [float(o.vehicle.body_type in ("sedan", "crossover", "suv")) for o in offers]
        elif key == "body_hatchback":
            col[key] = [float(o.vehicle.body_type == "hatchback") for o in offers]
        elif key == "compact":
            col[key] = [float(o.vehicle.body_type == "hatchback" or (o.vehicle.engine_cc or 9999) <= 1500) for o in offers]
        elif key == "clean_body":
            col[key] = [COND_SCORE.get(o.body_condition) for o in offers]
        elif key == "dual_fuel":
            col[key] = [float(o.fuel_type == "dual") for o in offers]
        elif key == "automatic":
            col[key] = [float(o.gearbox == "automatic") for o in offers]
        elif key.startswith("like:"):
            ref = _like_reference(key.split(":", 1)[1])
            col[key] = [0.0] * len(offers) if not ref else [
                float(o.vehicle.body_type == ref[0] and abs((o.fair_price or o.price) - ref[1]) <= 0.2 * ref[1])
                for o in offers
            ]
    return col


def deal_score(o: Offer) -> float:
    if o.exclusion or o.verdict == Offer.Verdict.UNKNOWN or o.p_cheaper is None:
        return 0.5
    if o.verdict == Offer.Verdict.SUSPICIOUS:
        return 0.0
    return o.p_cheaper


def rank(intent: dict) -> dict:
    c = intent["constraints"]
    main, over = candidates(c)
    everyone = main + over
    prefs = [{**p, "key": p["key"] if p["key"] != "like" else f"like:{p.get('value')}"} for p in intent["resolved_preferences"]]
    scores = preference_scores(prefs, everyone)
    ranked = []
    for idx, o in enumerate(everyone):
        breakdown = []
        for p in prefs:
            s = scores[p["key"]][idx]
            breakdown.append({"key": p["key"], "weight": WEIGHTS[p["strength"]], "score": 0.5 if s is None else round(s, 3),
                              "origin": p.get("origin", "explicit"), "known": s is not None})
        deal = deal_score(o)
        total = total_score(deal, [(b["weight"], b["score"]) for b in breakdown])
        ranked.append({"offer": o, "score": round(total, 4), "deal": round(deal, 3), "breakdown": breakdown,
                       "group": "main" if idx < len(main) else "over_budget"})

    def order(r):
        o = r["offer"]
        return (-r["score"], -CONFIDENCE_ORDER.get(o.confidence, 0), -(o.posted_at.timestamp() if o.posted_at else 0))

    main_r = sorted([r for r in ranked if r["group"] == "main"], key=order)
    over_r = sorted([r for r in ranked if r["group"] == "over_budget"], key=order)
    # The top pick is never suspicious or excluded.
    pick = next((i for i, r in enumerate(main_r)
                 if r["offer"].verdict != Offer.Verdict.SUSPICIOUS and not r["offer"].exclusion), None)
    if pick:
        main_r.insert(0, main_r.pop(pick))
    return {"main": main_r, "over_budget": over_r, "top_pick": main_r[0]["offer"].pk if pick is not None else None}
