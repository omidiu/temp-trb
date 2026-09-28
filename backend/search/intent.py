"""Intent: what the buyer is looking for — Constraints, Preferences and Needs.

The *explicit* Intent is what the buyer said (or edited via chips). `resolve()` expands Needs into
Preferences, merges duplicates at the stronger level, and drops Need-derived Preferences that
contradict something explicit (kept in `dropped` so the UI can show them crossed out).
"""

import copy

# Preference catalog: key → Persian label. Scoring lives in search/ranking.py.
PREFERENCES = {
    "cheaper": "ارزان‌تر",
    "newer": "مدل بالاتر",
    "low_mileage": "کم‌کارکرد",
    "low_fuel": "کم‌مصرف",
    "more_airbags": "ایربگ بیشتر",
    "has_abs": "ترمز ABS / ESC",
    "body_sedan": "بدنه سدان یا شاسی‌بلند",
    "body_hatchback": "بدنه هاچبک",
    "compact": "جمع‌وجور (هاچبک یا موتور کوچک)",
    "clean_body": "بدنه سالم‌تر",
    "dual_fuel": "دوگانه‌سوز",
    "automatic": "گیربکس اتوماتیک",
    "popular": "پرطرفدار (فروش راحت، قطعه ارزان)",
    "holds_value": "افت قیمت کمتر",
    "like": "مشابه",
}

NEEDS = {
    "family": {"label": "خانوادگی", "recipe": [("body_sedan", "strong"), ("more_airbags", "normal"),
               ("has_abs", "normal"), ("newer", "normal"), ("clean_body", "normal")]},
    "economical": {"label": "اقتصادی / کم‌مصرف", "recipe": [("low_fuel", "strong"), ("dual_fuel", "normal"),
                   ("cheaper", "normal"), ("popular", "normal")]},
    "city": {"label": "شهری", "recipe": [("compact", "normal"), ("automatic", "normal"), ("low_fuel", "normal")]},
    "ride_hailing": {"label": "تاکسی اینترنتی", "recipe": [("dual_fuel", "strong"), ("low_fuel", "normal"),
                     ("low_mileage", "normal"), ("popular", "normal"), ("body_sedan", "normal")]},
    "holds_value": {"label": "حفظ ارزش", "recipe": [("holds_value", "strong"), ("popular", "normal"),
                    ("clean_body", "normal"), ("newer", "normal")]},
}

# Model families the buyer can name → catalog `family` values.
FAMILIES = {
    "peugeot-206ir": "پژو ۲۰۶", "peugeot-206sd": "پژو ۲۰۶ صندوقدار", "peugeot-207": "پژو ۲۰۷",
    "peugeot-405": "پژو ۴۰۵", "peugeot-pars": "پژو پارس", "pride-111": "پراید ۱۱۱", "pride-131": "پراید ۱۳۱",
    "pride-132": "پراید ۱۳۲", "pride-141": "پراید ۱۴۱", "tiba": "تیبا", "dena": "دنا", "samand-lx": "سمند LX",
    "samand-soren": "سمند سورن", "quick": "کوییک", "shahin": "شاهین",
}

CONDITION_LABELS = {"clean": "بدون رنگ", "minor": "حداکثر رنگ جزئی"}

# Pairs that pull in opposite directions: an explicit one removes the Need-derived other.
CONFLICTS = {
    "body_sedan": {"body_hatchback", "compact"},
    "body_hatchback": {"body_sedan"},
    "compact": {"body_sedan"},
}


def empty_intent(text: str = "") -> dict:
    return {
        "text": text,
        "constraints": {
            "max_price": None, "min_price": None, "city": "tehran", "min_year": None, "max_year": None,
            "max_mileage": None, "models": [], "exclude_models": [], "gearbox": None, "fuel_type": None,
            "body_condition": None,
        },
        "preferences": [],       # [{key, strength, value?, span?}]
        "needs": [],             # [{key, span?, off: [pref keys switched off]}]
        "spans": {},             # constraint field → words it came from
        "source": "",            # "llm" | "keywords" | "edited"
    }


def _stronger(a: str, b: str) -> str:
    return "strong" if "strong" in (a, b) else "normal"


def resolve(intent: dict) -> dict:
    """Return a copy with `resolved_preferences` (what ranking uses) and `dropped` (crossed-out chips)."""
    intent = copy.deepcopy(intent)
    c = intent["constraints"]
    explicit = {}
    for p in intent.get("preferences", []):
        key = p["key"] if p["key"] != "like" else f"like:{p.get('value')}"
        if key in explicit:
            explicit[key]["strength"] = _stronger(explicit[key]["strength"], p.get("strength", "normal"))
        else:
            explicit[key] = {**p, "strength": p.get("strength", "normal"), "origin": "explicit"}

    resolved = dict(explicit)
    dropped = []
    for need in intent.get("needs", []):
        recipe = NEEDS.get(need["key"], {}).get("recipe", [])
        for key, strength in recipe:
            if key in need.get("off", []):
                continue
            reason = None
            if any(e in CONFLICTS.get(key, set()) for e in explicit):
                reason = "با خواستهٔ صریح شما در تضاد است"
            elif key == "automatic" and c.get("gearbox") == "manual":
                reason = "گیربکس دستی خواسته‌اید"
            elif key == "dual_fuel" and c.get("fuel_type") == "gasoline":
                reason = "بنزینی خواسته‌اید"
            if reason:
                dropped.append({"key": key, "need": need["key"], "reason": reason})
                continue
            if key in resolved:
                resolved[key]["strength"] = _stronger(resolved[key]["strength"], strength)
            else:
                resolved[key] = {"key": key, "strength": strength, "origin": f"need:{need['key']}"}
    intent["resolved_preferences"] = list(resolved.values())
    intent["dropped"] = dropped
    return intent
