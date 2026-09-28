"""Parse Bama's server-rendered spec pages (/car-reviews/...) into catalog rows."""

import re
from html import unescape

SPEC_ITEM = re.compile(
    r'<h3 class="spec-item__title"[^>]*>(?P<key>[^<]+)</h3>\s*'
    r'(?:<span class="spec-item__value"[^>]*>(?P<value>[^<]*)</span>|<svg[^>]*class="(?P<icon>check-icon|close-icon)")'
)
TITLE = re.compile(r"<title>\s*مشخصات فنی\s*(?P<name>.+?)\s*سال\s*(?P<y1>\d{4})\s*-\s*(?P<y2>\d{4})")


def spec_links(html: str, brand: str) -> list[str]:
    return sorted(set(re.findall(rf'href="(/car-reviews/{brand}/[a-z0-9]+-specs-[0-9a-z-]+)"', html)))


def parse_spec_page(html: str) -> dict:
    items = {}
    for m in SPEC_ITEM.finditer(html):
        key = unescape(m["key"]).strip()
        items[key] = m["value"].strip() if m["value"] is not None else (m["icon"] == "check-icon")
    t = TITLE.search(html)
    return {
        "name_fa": t["name"].strip() if t else "",
        "year_from": int(t["y1"]) if t else None,
        "year_to": int(t["y2"]) if t else None,
        "items": items,
    }


def _num(s):
    m = re.search(r"\d+(?:\.\d+)?", s or "")
    return float(m.group()) if m else None


def body_type(label: str) -> str:
    label = label or ""
    if "هاچ" in label:
        return "hatchback"
    if "کراس" in label:
        return "crossover"
    if "شاسی" in label or "SUV" in label:
        return "suv"
    if "سدان" in label:
        return "sedan"
    if "وانت" in label or "پیکاپ" in label:
        return "pickup"
    return "other"


def gearbox(label: str) -> str:
    label = label or ""
    if "اتوماتیک" in label or "CVT" in label.upper() or "DCT" in label.upper():
        return "automatic"
    if "دستی" in label:
        return "manual"
    return ""


def fuel_type(*labels: str) -> str:
    text = " ".join(l or "" for l in labels).lower()
    return "dual" if ("cng" in text or "دوگانه" in text) else "gasoline"


def to_row(parsed: dict) -> dict:
    it = parsed["items"]
    litres = _num(it.get("حجم موتور"))
    airbags = _num(it.get("مجموع ایربگ‌ها"))
    return {
        "year_from": parsed["year_from"],
        "year_to": parsed["year_to"],
        "body_type": body_type(it.get("نوع بدنه")),
        "body_label_fa": it.get("نوع بدنه", ""),
        "engine_cc": int(round(litres * 1000)) if litres else None,
        "engine_fa": it.get("پیشرانه", ""),
        "gearbox": gearbox(it.get("گیربکس")),
        "fuel_consumption": _num(it.get("مصرف ترکیبی")),
        "airbags": int(airbags) if airbags is not None else None,
        "abs": it.get("ترمز ضدقفل (ABS)") if isinstance(it.get("ترمز ضدقفل (ABS)"), bool) else None,
        "esc": it.get("کنترل پایداری (ESC)") if isinstance(it.get("کنترل پایداری (ESC)"), bool) else None,
    }
