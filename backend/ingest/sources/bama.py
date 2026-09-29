"""Bama: the web app's public JSON search, Tehran province. One request returns 30 full ads."""

from ingest import http
from ingest.models import RawListing

SEARCH_URL = "https://bama.ir/cad/api/search"

# Bama `vehicle` filter values. Note `peugeot,206` is silently ignored (returns every car): use `206ir`.
MODELS = [
    "peugeot,206ir", "peugeot,206sd", "peugeot,207", "peugeot,405", "peugeot,pars",
    "pride", "tiba", "dena", "samand", "quick", "shahin",
]


def crawl(cap: int, stdout=None, models=None) -> int:
    models = models or MODELS
    per_model = max(1, cap // len(models))
    total = 0
    for vehicle in models:
        got, page = 0, 0
        brand = vehicle.split(",")[0]
        while got < per_model:
            res = http.get(SEARCH_URL, params={"vehicle": vehicle, "region": "tehran", "pageIndex": page})
            res.raise_for_status()
            data = res.json()
            ads = [a for a in (data.get("data") or {}).get("ads", []) if a.get("type") == "ad" and a.get("detail")]
            if not ads:
                break
            for ad in ads:
                d = ad["detail"]
                # Guard against an ignored filter returning every car.
                if d.get("brand") != brand and brand not in d.get("url", ""):
                    continue
                if got >= per_model:
                    break
                _, created = RawListing.objects.get_or_create(
                    source="bama", source_id=d["code"],
                    defaults={"url": "https://bama.ir" + d["url"], "payload": ad},
                )
                got += created
            # Bama's total_count is fake; stop when a page comes back short or has_next is false.
            if not (data.get("metadata") or {}).get("has_next") or len(ads) < 30:
                break
            page += 1
        total += got
        if stdout:
            stdout.write(f"bama {vehicle}: +{got}")
    return total
