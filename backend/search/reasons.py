"""One-line, template-only reason per ranked Offer (no LLM)."""

from market.models import ModelStats, Offer

from . import fa
from .intent import FAMILIES, PREFERENCES


def deal_phrase(o: Offer) -> str | None:
    if o.exclusion or not o.fair_price:
        return None
    diff = o.fair_price - o.price
    if o.verdict == Offer.Verdict.SUSPICIOUS:
        return "⚠️ بیش از ۲۵٪ زیر قیمت منصفانه — احتیاط"
    if o.verdict == Offer.Verdict.GREAT:
        return f"{fa.toman(diff)} زیر قیمت منصفانه"
    if o.verdict == Offer.Verdict.OVERPRICED:
        return f"{fa.toman(-diff)} بالای قیمت منصفانه"
    return None


def pref_phrase(key: str, score: float, o: Offer, stats: dict) -> str:
    v = o.vehicle
    if key == "cheaper":
        return f"ارزان‌تر از {fa.pct(score)} گزینه‌ها"
    if key == "newer":
        return f"مدل {fa.num(o.year)}"
    if key == "low_mileage":
        return f"{fa.num(o.mileage)} کیلومتر کارکرد"
    if key == "low_fuel" and v.fuel_consumption:
        return f"مصرف {fa.num(v.fuel_consumption)} لیتر"
    if key == "more_airbags" and v.airbags:
        return f"{fa.num(v.airbags)} ایربگ"
    if key == "holds_value":
        d = getattr(stats.get(v.family), "depreciation", None)
        if d is not None:
            return f"افت قیمت حدود {fa.pct(d)} در سال"
    if key.startswith("like:"):
        return f"مشابه {FAMILIES.get(key.split(':', 1)[1], '')}"
    if key == "clean_body":
        return "بدون رنگ" if o.body_condition == "clean" else "بدنه نسبتاً سالم"
    return PREFERENCES.get(key, key)


def one_line(r: dict, stats: dict | None = None) -> str:
    stats = stats if stats is not None else {m.model_key: m for m in ModelStats.objects.all()}
    o = r["offer"]
    parts = []
    if (d := deal_phrase(o)):
        parts.append(d)
    best = sorted((b for b in r["breakdown"] if b["known"] and b["score"] >= 0.75),
                  key=lambda b: -b["weight"] * b["score"])
    for b in best[: 2 if parts else 3]:
        parts.append(pref_phrase(b["key"], b["score"], o, stats))
    return "، ".join(parts)
