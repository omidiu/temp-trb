"""Free Persian text → explicit Intent.

The LLM only points at words: it returns which Constraints/Preferences/Needs the text contains and
the exact phrase each came from. Numbers are always parsed by our code from those phrases. When the
LLM is unavailable, a keyword/regex parser covers price, year, mileage, models, gearbox, fuel,
condition, common Preferences and Need keywords.
"""

import logging
import re

from llm import client as llm
from market.text import latin_digits, norm, parse_amount, parse_int

from .intent import FAMILIES, NEEDS, PREFERENCES, empty_intent

log = logging.getLogger(__name__)

# ---------- keyword fallback ----------

MODEL_WORDS = [  # longest first
    ("۲۰۶ صندوقدار", ["peugeot-206sd"]), ("206 sd", ["peugeot-206sd"]), ("۲۰۶ sd", ["peugeot-206sd"]),
    ("پراید ۱۱۱", ["pride-111"]), ("پراید ۱۳۱", ["pride-131"]), ("پراید ۱۳۲", ["pride-132"]), ("پراید ۱۴۱", ["pride-141"]),
    ("سمند سورن", ["samand-soren"]), ("سورن", ["samand-soren"]), ("سمند", ["samand-lx", "samand-soren"]),
    ("پراید", ["pride-111", "pride-131", "pride-132", "pride-141"]),
    ("۲۰۶", ["peugeot-206ir", "peugeot-206sd"]), ("۲۰۷", ["peugeot-207"]), ("۴۰۵", ["peugeot-405"]),
    ("پارس", ["peugeot-pars"]), ("تیبا", ["tiba"]), ("دنا", ["dena"]), ("کوییک", ["quick"]), ("کوئیک", ["quick"]),
    ("شاهین", ["shahin"]),
]
NEED_WORDS = {
    "family": ["خانوادگی", "خانواده"], "economical": ["اقتصادی", "به صرفه"],
    "city": ["شهری", "توی شهر", "داخل شهر"], "ride_hailing": ["اسنپ", "تپسی", "تاکسی اینترنتی", "مسافرکشی"],
    "holds_value": ["حفظ ارزش", "سرمایه", "ضرر نکنم", "ارزش خرید"],
}
PREF_WORDS = {
    "low_fuel": ["کم مصرف", "کم‌مصرف", "مصرف کم", "مصرف پایین"], "cheaper": ["ارزون", "ارزان"],
    "low_mileage": ["کم کارکرد", "کارکرد کم", "کم‌کارکرد"], "newer": ["مدل بالا", "مدل جدید", "هرچی نوتر"],
    "more_airbags": ["ایربگ"], "has_abs": ["abs", "ترمز ضد قفل"], "dual_fuel": ["دوگانه"],
    "automatic": ["اتومات"], "body_hatchback": ["هاچبک", "هاچ بک"], "body_sedan": ["سدان", "صندوقدار", "شاسی بلند"],
    "clean_body": ["بدنه سالم", "سالم باشه"], "popular": ["پرطرفدار", "قطعه ارزون", "فروش راحت"],
    "holds_value": ["افت قیمت کم"],
}
STRONG = ["خیلی", "حتما", "حتماً", "واقعا", "حتمن"]
HARD = ["فقط", "حتما", "حتماً"]
NEG = ["نه ", "به جز", "بجز", "غیر از", "نمیخوام", "نمی‌خوام", "نباشه"]


def _near(t: str, idx: int, words, before=12) -> bool:
    window = t[max(0, idx - before): idx]
    return any(w in window for w in words)


def keyword_parse(text: str) -> dict:
    intent = empty_intent(text)
    intent["source"] = "keywords"
    c, spans = intent["constraints"], intent["spans"]
    t = norm(text)
    t_lat = latin_digits(t)

    # price: "تا / زیر / حداکثر / کمتر از X" → max; "بالای / حداقل / از X" (with a unit) → min
    for m in re.finditer(r"(تا|زیر|حداکثر|کمتر از|نهایتا|بودجه|بودجم|بودجه ام)\s*(?:حدود\s*)?([\d.,/]+\s*(?:میلیارد|میلیون|م)(?![آ-ی])|(?:یک|دو|سه)\s*(?:و\s*نیم\s*)?(?:میلیارد|میلیون))", t_lat):
        amount = parse_amount(m.group(2))
        if amount:
            c["max_price"], spans["max_price"] = amount, m.group(0)
            break
    m = re.search(r"(بالای|حداقل|بیشتر از)\s*([\d.,/]+\s*(?:میلیارد|میلیون))", t_lat)
    if m and parse_amount(m.group(2)):
        c["min_price"], spans["min_price"] = parse_amount(m.group(2)), m.group(0)

    # year: "مدل ۹۸ به بالا", "بالای ۹۸", "از ۱۳۹۸ به بعد"
    m = re.search(r"(?:مدل|سال)?\s*(1[34]\d\d|\d\d)\s*(?:به بالا|به بعد|ببعد|بالاتر)", t_lat) or \
        re.search(r"(?:مدل\s*)?(?:بالای|بعد از|از)\s*(?:مدل\s*)?(1[34]\d\d|\d\d)(?!\s*(?:هزار|میلیون|میلیارد|م\b|کیلومتر))", t_lat)
    if m:
        y = int(m.group(1))
        c["min_year"] = y if y > 1000 else (1300 + y if y >= 50 else 1400 + y)
        spans["min_year"] = m.group(0).strip()

    # mileage: "زیر ۵۰ هزار کیلومتر", "کارکرد کمتر از ۱۰۰ هزار"
    m = re.search(r"(?:زیر|کمتر از|حداکثر|تا)\s*(\d+)\s*(هزار)?\s*(?:کیلومتر|کارکرد|km)", t_lat) or \
        re.search(r"کارکرد\s*(?:زیر|کمتر از|حداکثر|تا)\s*(\d+)\s*(هزار)?", t_lat)
    if m:
        c["max_mileage"] = int(m.group(1)) * (1000 if m.group(2) else 1)
        spans["max_mileage"] = m.group(0)

    # models
    taken = t
    for word, fams in MODEL_WORDS:
        w = norm(word)
        idx = taken.find(w)
        if idx < 0:
            continue
        if _near(taken, idx, ["مثل", "شبیه"]):
            for f in fams[:1]:
                intent["preferences"].append({"key": "like", "value": f, "strength": "normal", "span": word})
        elif _near(taken, idx, NEG, before=10) or re.match(r"\s*(نباشه|نمیخوام|نه)", taken[idx + len(w):]):
            c["exclude_models"] += [f for f in fams if f not in c["exclude_models"]]
        else:
            c["models"] += [f for f in fams if f not in c["models"]]
        taken = taken[:idx] + " " * len(w) + taken[idx + len(w):]

    # gearbox / fuel / condition constraints
    if re.search(r"(فقط|حتما|حتماً)\s*اتومات", t):
        c["gearbox"], spans["gearbox"] = "automatic", "فقط اتوماتیک"
    elif re.search(r"(فقط|حتما)\s*(دنده ای|دستی)", t):
        c["gearbox"], spans["gearbox"] = "manual", "فقط دنده‌ای"
    if re.search(r"(فقط|حتما)\s*دوگانه", t):
        c["fuel_type"], spans["fuel_type"] = "dual", "فقط دوگانه‌سوز"
    if re.search(r"(بدون رنگ|بی رنگ)", t):
        c["body_condition"], spans["body_condition"] = "clean", "بدون رنگ"
    elif re.search(r"(تصادفی نباشه|بدون تصادف|تصادف نداشته)", t):
        c["body_condition"], spans["body_condition"] = "minor", "بدون تصادف"

    # needs
    for key, words in NEED_WORDS.items():
        w = next((w for w in words if w in t), None)
        if w:
            intent["needs"].append({"key": key, "span": w, "off": []})

    # soft preferences (skip ones already hard)
    hard = {"automatic": c["gearbox"] == "automatic", "dual_fuel": c["fuel_type"] == "dual",
            "clean_body": c["body_condition"] is not None}
    for key, words in PREF_WORDS.items():
        if hard.get(key):
            continue
        for w in words:
            idx = t.find(norm(w))
            if idx >= 0:
                strength = "strong" if _near(t, idx, STRONG) else "normal"
                intent["preferences"].append({"key": key, "strength": strength, "span": w.strip()})
                break
    return intent


# ---------- LLM ----------

SYSTEM = """You turn a Persian used-car buyer's request into structured search intent for Tehran's used-car market.
Rules:
- Only numbers the buyer actually typed become constraints. Vague words ("ارزون", "کم‌کارکرد", "مدل بالا") are preferences, never invented numbers.
- Budget ceilings, cities, and anything with "فقط", "حتماً" or a negation ("نه", "به جز") are constraints.
- Named models are a models constraint; "مثل X"/"شبیه X" is a `like` preference for X instead.
- Intensifiers ("خیلی", "حتماً", "واقعاً") make a preference strong.
- Map situations to needs: family, economical, city, ride_hailing (اسنپ/تپسی), holds_value.
- For every item copy the exact words from the text it came from into `span`. Put number phrases (e.g. "تا ۸۰۰ میلیون", "مدل ۹۸ به بالا", "زیر ۱۰۰ هزار کیلومتر") into the matching *_span field; do not convert them."""

_str_or_null = {"type": ["string", "null"]}
SCHEMA = {
    "type": "object",
    "properties": {
        "max_price_span": _str_or_null, "min_price_span": _str_or_null,
        "min_year_span": _str_or_null, "max_year_span": _str_or_null, "max_mileage_span": _str_or_null,
        "models": {"type": "array", "items": {"type": "string", "enum": list(FAMILIES)}},
        "exclude_models": {"type": "array", "items": {"type": "string", "enum": list(FAMILIES)}},
        "gearbox": {"type": ["string", "null"], "enum": ["manual", "automatic", None]},
        "fuel_type": {"type": ["string", "null"], "enum": ["dual", "gasoline", None]},
        "body_condition": {"type": ["string", "null"], "enum": ["clean", "minor", None]},
        "preferences": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "enum": list(PREFERENCES)},
                "strength": {"type": "string", "enum": ["normal", "strong"]},
                "like_model": {"type": ["string", "null"], "enum": list(FAMILIES) + [None]},
                "span": {"type": "string"},
            },
            "required": ["key", "strength", "like_model", "span"], "additionalProperties": False,
        }},
        "needs": {"type": "array", "items": {
            "type": "object",
            "properties": {"key": {"type": "string", "enum": list(NEEDS)}, "span": {"type": "string"}},
            "required": ["key", "span"], "additionalProperties": False,
        }},
    },
    "required": ["max_price_span", "min_price_span", "min_year_span", "max_year_span", "max_mileage_span",
                 "models", "exclude_models", "gearbox", "fuel_type", "body_condition", "preferences", "needs"],
    "additionalProperties": False,
}

FAMILY_HINT = "\n".join(f"{k}: {v}" for k, v in FAMILIES.items())


def _year(span):
    m = re.search(r"(1[34]\d\d|\d\d)", latin_digits(span or ""))
    if not m:
        return None
    y = int(m.group(1))
    return y if y > 1000 else (1300 + y if y >= 50 else 1400 + y)


def _mileage(span):
    t = latin_digits(span or "")
    n = parse_int(re.search(r"\d[\d,]*", t).group()) if re.search(r"\d", t) else None
    return n * 1000 if n is not None and "هزار" in t else n


def llm_parse(text: str) -> dict:
    out = llm.complete_json(f"Model families:\n{FAMILY_HINT}\n\nBuyer's text:\n{text}", system=SYSTEM, schema=SCHEMA, max_tokens=1200)
    intent = empty_intent(text)
    intent["source"] = "llm"
    c, spans = intent["constraints"], intent["spans"]
    for field, parse in [("max_price", parse_amount), ("min_price", parse_amount), ("min_year", _year),
                         ("max_year", _year), ("max_mileage", _mileage)]:
        span = out.get(f"{field}_span")
        # The span must really be in the text, and the number is parsed by us.
        if span and norm(span) in norm(text):
            value = parse(span)
            if value:
                c[field], spans[field] = value, span
    c["models"] = [m for m in out.get("models", []) if m in FAMILIES]
    c["exclude_models"] = [m for m in out.get("exclude_models", []) if m in FAMILIES]
    for field in ("gearbox", "fuel_type", "body_condition"):
        c[field] = out.get(field)
    for p in out.get("preferences", []):
        pref = {"key": p["key"], "strength": p["strength"], "span": p.get("span", "")}
        if p["key"] == "like":
            if not p.get("like_model"):
                continue
            pref["value"] = p["like_model"]
        intent["preferences"].append(pref)
    intent["needs"] = [{"key": n["key"], "span": n.get("span", ""), "off": []} for n in out.get("needs", [])]
    return intent


def parse(text: str) -> dict:
    if llm.available():
        try:
            return llm_parse(text)
        except llm.LLMUnavailable as e:
            log.warning("Intent LLM parse failed, using keywords: %s", e)
    return keyword_parse(text)
