"""Explain the top pick (and why not #2 and #3) from a fact sheet built out of the ranking numbers.

The LLM writes the prose; a grounding check rejects any number that isn't in the fact sheet and any
car model that isn't one of the three. On failure — or without an LLM — a template writes the same
facts. Either way the explanation can't claim what the numbers don't support.
"""

import json
import re

from llm import client as llm
from market.models import Offer
from market.text import latin_digits

from . import fa
from .intent import CONDITION_LABELS, FAMILIES, NEEDS, PREFERENCES

BRAND_WORDS = ["پژو", "پراید", "تیبا", "دنا", "سمند", "سورن", "کوییک", "شاهین", "پارس", "رانا", "ساینا", "هایما", "جک"]
VERDICT_FA = {"great": "زیر قیمت", "fair": "منصفانه", "overpriced": "گران", "suspicious": "مشکوک", "unknown": "بدون داوری"}


def _pref_label(key: str) -> str:
    return f"مشابه {FAMILIES.get(key[5:], '')}" if key.startswith("like:") else PREFERENCES.get(key, key)


def intent_summary(intent: dict) -> list[str]:
    c, out = intent["constraints"], []
    if c.get("max_price"):
        out.append(f"بودجه تا {fa.toman(c['max_price'])} تومان")
    if c.get("min_year"):
        out.append(f"مدل {fa.num(c['min_year'])} به بالا")
    if c.get("max_mileage"):
        out.append(f"کارکرد حداکثر {fa.num(c['max_mileage'])} کیلومتر")
    if c.get("gearbox"):
        out.append("فقط اتوماتیک" if c["gearbox"] == "automatic" else "فقط دنده‌ای")
    if c.get("fuel_type") == "dual":
        out.append("فقط دوگانه‌سوز")
    if c.get("body_condition"):
        out.append(CONDITION_LABELS[c["body_condition"]])
    if c.get("models"):
        out.append("فقط " + "، ".join(FAMILIES[m] for m in c["models"]))
    for n in intent.get("needs", []):
        out.append(f"نیاز: {NEEDS[n['key']]['label']}")
    for p in intent.get("preferences", []):
        label = _pref_label(p["key"] if p["key"] != "like" else f"like:{p.get('value')}")
        out.append(label + (" (مهم)" if p.get("strength") == "strong" else ""))
    return out


def _offer_facts(r: dict) -> dict:
    o: Offer = r["offer"]
    facts = {
        "id": o.pk,
        "name": o.vehicle.name_fa,
        "model_year": fa.digits(o.year),
        "mileage_km": fa.num(o.mileage),
        "price": fa.toman(o.price) + " تومان",
        "verdict": VERDICT_FA[o.verdict] if not o.exclusion else "بدون داوری",
        "match_score": fa.pct(r["score"]),
    }
    if o.fair_price and not o.exclusion:
        facts.update(
            fair_price=fa.toman(o.fair_price) + " تومان",
            comparables=fa.num(len(o.comparable_ids)),
            cheaper_than_share_of_comparables=fa.pct(o.p_cheaper or 0),
            difference_from_fair_price=fa.toman(abs(o.fair_price - o.price)) + " تومان " + ("کمتر" if o.price <= o.fair_price else "بیشتر"),
        )
    return facts


def fact_sheet(intent: dict, rows: list[dict]) -> dict:
    top = rows[0]
    contributors = sorted((b for b in top["breakdown"] if b["known"]), key=lambda b: -b["weight"] * b["score"])[:3]
    sheet = {
        "buyer_wants": intent_summary(intent),
        "top_pick": {**_offer_facts(top),
                     "strongest_matches": [{"preference": _pref_label(b["key"]), "score": fa.pct(b["score"])} for b in contributors]},
        "runners_up": [],
    }
    top_scores = {b["key"]: b for b in top["breakdown"]}
    for rank_no, r in enumerate(rows[1:3], start=2):
        facts = {**_offer_facts(r), "rank": fa.num(rank_no)}
        # Where it lost the most against the top pick: the deal, or the Preference with the biggest weighted gap.
        gaps = [(2 * (top["deal"] - r["deal"]), "منصفانه بودن قیمت", top["deal"], r["deal"])]
        for b in r["breakdown"]:
            t = top_scores.get(b["key"])
            if t:
                gaps.append((b["weight"] * (t["score"] - b["score"]), _pref_label(b["key"]), t["score"], b["score"]))
        gap = max(gaps, key=lambda g: g[0])
        if gap[0] > 0:
            facts["lost_most_on"] = {"aspect": gap[1], "top_pick_score": fa.pct(gap[2]), "this_score": fa.pct(gap[3])}
        sheet["runners_up"].append(facts)
    return sheet


# ---------- template ----------

def template(sheet: dict) -> str:
    t = sheet["top_pick"]
    parts = [f"«{t['name']}» مدل {t['model_year']} با {t['mileage_km']} کیلومتر کارکرد بهترین گزینه برای شماست."]
    if "fair_price" in t:
        if t["verdict"] == "زیر قیمت":
            parts.append(f"قیمتش {t['price']} است، یعنی {t['difference_from_fair_price']} از میانهٔ {t['comparables']} خودروی مشابه ({t['fair_price']}) و ارزان‌تر از {t['cheaper_than_share_of_comparables']} آن‌ها.")
        elif t["verdict"] == "گران":
            parts.append(f"قیمتش {t['price']} کمی بالاتر از میانهٔ {t['comparables']} خودروی مشابه ({t['fair_price']}) است، اما بهتر از بقیه با خواسته‌های شما جور است.")
        else:
            parts.append(f"قیمتش {t['price']} در محدودهٔ منصفانه است (میانهٔ {t['comparables']} خودروی مشابه: {t['fair_price']}).")
    else:
        parts.append(f"قیمتش {t['price']} است؛ برای سنجیدن قیمت این مدل خودروی مشابه کافی نداشتیم.")
    if t["strongest_matches"]:
        parts.append("بیشترین تطابق با خواسته‌هایتان: " + "، ".join(f"{m['preference']} ({m['score']})" for m in t["strongest_matches"]) + ".")
    for r in sheet["runners_up"]:
        if "lost_most_on" in r:
            l = r["lost_most_on"]
            parts.append(f"«{r['name']}» ({r['price']}) رتبهٔ {r['rank']} شد، چون در «{l['aspect']}» ضعیف‌تر بود ({l['this_score']} در برابر {l['top_pick_score']}).")
    return " ".join(parts)


# ---------- grounding ----------

def _numbers(text: str) -> set[str]:
    t = latin_digits(text).replace("٫", ".").replace("٬", "").replace(",", "")
    return set(re.findall(r"\d+(?:\.\d+)?", t))


def grounded(text: str, sheet: dict) -> bool:
    allowed = _numbers(json.dumps(sheet, ensure_ascii=False)) | {"1", "2", "3"}
    if not _numbers(text) <= allowed:
        return False
    names = " ".join([sheet["top_pick"]["name"]] + [r["name"] for r in sheet["runners_up"]])
    # Every car brand/model word mentioned must belong to one of the three Offers.
    return all(w in names for w in BRAND_WORDS if w in text)


SYSTEM = """You write a short Persian explanation (3–5 sentences, plain text, no lists, no markdown) of why the top pick is the best used car for this buyer, and briefly why the runners-up ranked lower.
Use ONLY the facts in the JSON. Copy numbers exactly as written there (Persian digits); do not compute, round or invent any number, and do not mention any car that is not in the JSON.
Mention the price verdict against similar cars, the buyer's preferences it matches best, and where each runner-up fell short. Address the buyer as «شما»."""


def explain(intent: dict, rows: list[dict]) -> dict:
    if not rows or rows[0]["offer"].verdict == Offer.Verdict.SUSPICIOUS or rows[0]["offer"].exclusion:
        return {"text": "", "method": "none", "fact_sheet": None}
    sheet = fact_sheet(intent, rows)
    if llm.available():
        try:
            from django.conf import settings
            text = llm.complete(json.dumps(sheet, ensure_ascii=False, indent=1), system=SYSTEM,
                                model=settings.LLM_MODEL_WRITER, max_tokens=800).strip()
            if text and grounded(text, sheet):
                return {"text": text, "method": "llm", "fact_sheet": sheet}
        except llm.LLMUnavailable:
            pass
        return {"text": template(sheet), "method": "template_after_llm_rejected", "fact_sheet": sheet}
    return {"text": template(sheet), "method": "template", "fact_sheet": sheet}
