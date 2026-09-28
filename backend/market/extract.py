"""Per-Source extraction: RawListing payload → plain dict of Listing fields."""

from datetime import datetime, timedelta, timezone

from . import rules
from .text import parse_int, parse_year


def divar(payload: dict) -> dict:
    post, row = payload["post"], payload.get("row") or {}
    we = post.get("webengage") or {}
    info, scores, description = {}, {}, ""
    for section in post.get("sections", []):
        for w in section.get("widgets", []):
            t, d = w.get("widget_type"), w.get("data") or {}
            if t == "GROUP_INFO_ROW":
                info.update({i["title"]: i["value"] for i in d.get("items", [])})
            elif t == "UNEXPANDABLE_ROW":
                info[d.get("title", "")] = d.get("value", "")
            elif t == "SCORE_ROW":
                scores[d.get("title", "")] = d.get("descriptive_score", "")
            elif t == "DESCRIPTION_ROW" and not description:
                description = d.get("text", "")
    seo = post.get("seo") or {}
    title = (seo.get("web_info") or {}).get("title") or row.get("title", "")
    price = we.get("price") or parse_int(info.get("قیمت پایه"))
    posted_at = None
    if seo.get("unavailable_after"):
        # Divar posts expire 31 days after (re)posting.
        posted_at = datetime.fromisoformat(seo["unavailable_after"]).replace(tzinfo=timezone.utc) - timedelta(days=31)
    chassis = [v for k, v in scores.items() if "شاسی" in k]
    return {
        "title": title,
        "description": description,
        "raw_name": we.get("brand_model", ""),
        "year": parse_year(info.get("مدل (سال تولید)")) or parse_year(title),
        "mileage": parse_int(info.get("کارکرد")),
        "price": price or None,
        "gearbox": rules.gearbox(info.get("گیربکس", "")),
        "fuel_type": rules.fuel(info.get("نوع سوخت", "")),
        "body_condition": rules.body_condition(scores.get("بدنه", ""), *chassis),
        "body_condition_raw": " / ".join(f"{k}: {v}" for k, v in scores.items() if k != "موتور"),
        "exclusion": rules.exclusion(title, description, price),
        "city": "tehran",
        "posted_at": posted_at,
        "image_url": row.get("image_url", ""),
    }


EXTRACTORS = {"divar": divar}
