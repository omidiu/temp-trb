"""Rule-based field mapping. The LLM (ticket 04) only fills gaps these leave."""

from .models import BodyCondition, Exclusion
from .text import norm

_MAJOR = ["تصادفی", "دور رنگ", "دوررنگ", "تمام رنگ", "کامل رنگ", "اوراقی", "چند لکه", "چند ناحیه", "سوختگی", "ضربه", "تعویض"]
_MINOR = ["یک لکه", "دو لکه", "گلگیر رنگ", "رنگ شدگی", "رنگ‌شدگی", "لکه رنگ", "رنگ"]
_CLEAN = ["بدون رنگ", "بی رنگ", "سالم", "خط و خش", "صافکاری بی رنگ", "صافکاری بدون رنگ"]


def body_condition(body: str, *chassis: str) -> str:
    """Map seller-declared body/chassis labels to clean/minor/major; '' when unknown."""
    b = norm(body)
    for c in chassis:
        c = norm(c)
        if c and any(k in c for k in ["ضربه", "تعویض", "رنگ", "جوش"]):
            return BodyCondition.MAJOR
    if not b:
        return ""
    if any(k in b for k in ["صافکاری بی رنگ", "صافکاری بدون رنگ", "بدون رنگ", "بی رنگ"]):
        return BodyCondition.CLEAN
    if any(k in b for k in _MAJOR):
        return BodyCondition.MAJOR
    if any(k in b for k in _MINOR):
        return BodyCondition.MINOR
    if any(k in b for k in _CLEAN):
        return BodyCondition.CLEAN
    return ""


PLACEHOLDER_BELOW = 50_000_000  # toman; nothing in scope sells this cheap


def exclusion(title: str, description: str, price: int | None) -> str:
    t = norm(f"{title} {description}")
    if any(k in t for k in ["حواله", "پیش فروش", "پیشفروش", "ثبت نام"]):
        return Exclusion.PRESALE
    if any(k in t for k in ["قسطی", "اقساط", "لیزینگ", "لیزینگی", "پیش پرداخت"]):
        return Exclusion.INSTALMENT
    if not price or price < PLACEHOLDER_BELOW:
        return Exclusion.PLACEHOLDER
    return ""


def gearbox(label: str) -> str:
    t = norm(label)
    if "اتومات" in t or "cvt" in t.lower():
        return "automatic"
    if "دنده" in t or "دستی" in t:
        return "manual"
    return ""


def fuel(label: str) -> str:
    t = norm(label)
    if "دوگانه" in t or "cng" in t.lower() or "گاز" in t:
        return "dual"
    if "بنزین" in t:
        return "gasoline"
    return ""
