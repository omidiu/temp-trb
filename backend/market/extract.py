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


def bama(payload: dict) -> dict:
    d, price_info = payload["detail"], payload.get("price") or {}
    # URL: /car/detail-<code>-<brand>-<model>-<trim>-<year>; the middle is Bama's trim slug.
    parts = (d.get("url") or "").split("-")
    raw_name = "-".join(parts[2:-1]) if len(parts) > 3 else ""
    price = parse_int(price_info.get("price")) or None
    price_type = price_info.get("type", "")
    title = f"{(d.get('title') or '').replace('،', '')} {d.get('trim') or ''} مدل {d.get('year') or ''}".strip()
    description = d.get("description") or ""
    exclusion = rules.exclusion(title, description, price)
    if price_type not in ("lumpsum", "negotiable", "") and not exclusion:
        exclusion = "instalment"  # Bama's own price type says the shown price isn't the full price
    location = d.get("location") or ""
    mileage_text = d.get("mileage") or ""
    posted = d.get("modified_date")
    return {
        "title": title,
        "description": description,
        "raw_name": raw_name,
        "year": parse_year(d.get("year")),
        "mileage": 0 if "صفر" in mileage_text else parse_int(mileage_text),
        "price": price,
        "gearbox": rules.gearbox(d.get("transmission") or ""),
        "fuel_type": rules.fuel(d.get("fuel") or ""),
        "body_condition": rules.body_condition(d.get("body_status") or ""),
        "body_condition_raw": d.get("body_status") or "",
        "exclusion": exclusion,
        "city": "tehran" if location.startswith("تهران") else "other",
        "posted_at": datetime.fromisoformat(posted).replace(tzinfo=timezone.utc) if posted else None,
        "image_url": d.get("image") or "",
    }


EXTRACTORS = {"divar": divar, "bama": bama}
