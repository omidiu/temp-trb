"""Divar: the web app's public JSON endpoints, Tehran, passenger cars. No login, no phone numbers."""

import logging

import httpx

from ingest import http
from ingest.models import RawListing

log = logging.getLogger(__name__)

SEARCH_URL = "https://api.divar.ir/v8/postlist/w/search"
POST_URL = "https://api.divar.ir/v8/posts-v2/web/{token}"
TEHRAN = "1"

# Divar brand_model filter values for the in-scope models.
MODELS = [
    "Peugeot 206", "Peugeot 207i", "Peugeot 405", "Peugeot Pars", "Pride",
    "Tiba", "Dena", "Samand", "Quick", "Shahin",
]


def _search(brand_model: str, pagination_data=None) -> dict:
    body = {
        "city_ids": [TEHRAN],
        "search_data": {"form_data": {"data": {
            "category": {"str": {"value": "light"}},
            "brand_model": {"repeated_string": {"value": [brand_model]}},
        }}},
    }
    if pagination_data:
        body["pagination_data"] = pagination_data
    res = http.post(SEARCH_URL, json=body)
    res.raise_for_status()
    return res.json()


def crawl(cap: int, stdout=None, models=None) -> int:
    """Fetch up to `cap` new Listings, spread evenly over MODELS (or `models`). Resumable: known tokens are skipped."""
    models = models or MODELS
    per_model = max(1, cap // len(models))
    total = 0
    for brand_model in models:
        got, pagination, mismatches = 0, None, 0
        while got < per_model and mismatches < 15:
            data = _search(brand_model, pagination)
            rows = [w["data"] for w in data.get("list_widgets", []) if w.get("widget_type") == "POST_ROW"]
            for row in rows:
                if got >= per_model:
                    break
                token = row.get("token") or row["action"]["payload"]["token"]
                if RawListing.objects.filter(source="divar", source_id=token).exists():
                    continue
                try:
                    res = http.get(POST_URL.format(token=token))
                except httpx.TransportError as e:
                    log.warning("divar post %s: %s (skipped)", token, e)
                    continue
                if res.status_code != 200:
                    log.warning("divar post %s: HTTP %s", token, res.status_code)
                    continue
                post = res.json()
                # An unknown filter value can silently return every car; keep only the asked-for model.
                if not (post.get("webengage") or {}).get("brand_model", "").startswith(brand_model):
                    mismatches += 1
                    continue
                mismatches = 0
                RawListing.objects.create(
                    source="divar", source_id=token, url=f"https://divar.ir/v/{token}",
                    payload={"row": row, "post": post},
                )
                got += 1
            page = data.get("pagination") or {}
            if not rows or not page.get("has_next_page"):
                break
            pagination = page.get("data")
        total += got
        if stdout:
            stdout.write(f"divar {brand_model}: +{got}")
    return total
