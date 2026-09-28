"""One-off: build catalog/data/vehicles.seed.json from Bama's spec pages.

The output is meant to be reviewed by hand and committed; `load_catalog` reads it.
"""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.bama_specs import fuel_type, parse_spec_page, spec_links, to_row
from ingest import http

BASE = "https://bama.ir"
SEED = Path(__file__).resolve().parents[2] / "data" / "vehicles.seed.json"

# brand slug → (Persian make, wanted Bama model slugs or None for all)
WANTED = {
    "peugeot": ("پژو", {"206ir", "206sd", "405", "pars", "207"}),
    "pride": ("پراید", {"111", "131", "132", "141"}),
    "tiba": ("تیبا", None),
    "dena": ("دنا", None),
    "samand": ("سمند", {"lx", "soren"}),
    "quick": ("کوییک", None),
    "shahin": ("شاهین", None),
}
# For these brands every Bama "model" is a variant of one car, so market stats group by brand.
FAMILY_IS_BRAND = {"tiba", "dena", "quick", "shahin"}


class Command(BaseCommand):
    help = "Fetch Bama spec pages for in-scope models and write the catalog seed JSON."

    def handle(self, *args, **options):
        rows = []
        for brand, (make_fa, wanted) in WANTED.items():
            index = http.get(f"{BASE}/car-reviews/{brand}").text
            by_model = {}
            for link in spec_links(index, brand):
                model = re.match(rf"/car-reviews/{brand}/([a-z0-9]+)-specs-", link)[1]
                by_model.setdefault(model, link)
            for model, first in sorted(by_model.items()):
                if wanted is not None and model not in wanted:
                    continue
                rows += self._model_rows(brand, make_fa, model, first)
                self.stdout.write(f"{brand}/{model}: {len(rows)} rows so far")
        SEED.parent.mkdir(parents=True, exist_ok=True)
        SEED.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
        self.stdout.write(self.style.SUCCESS(f"{len(rows)} trims written to {SEED}"))

    def _model_rows(self, brand, make_fa, model, first_link):
        html = http.get(BASE + first_link).text
        prefix = re.match(r"(/car-reviews/[a-z0-9]+/[a-z0-9]+-specs-\d+)", first_link)[1]
        trims = {}
        for m in re.finditer(rf'href="({re.escape(prefix)}-([0-9a-z-]+))"[^>]*>(.*?)</a>', html, re.S):
            trims.setdefault(m[2], (m[1], re.sub(r"<[^>]+>", "", m[3]).strip()))
        if not trims:  # model without trims: the page itself is the only row
            trims = {"": (first_link, "")}
        out = []
        for trim, (url, trim_fa) in sorted(trims.items()):
            page = html if url == first_link else http.get(BASE + url).text
            parsed = parse_spec_page(page)
            name_fa = parsed["name_fa"]
            model_fa = name_fa[: -len(trim_fa)].strip() if trim_fa and name_fa.endswith(trim_fa) else name_fa
            row = {
                "id": "-".join(p for p in [brand, model, trim] if p),
                "make": brand, "make_fa": make_fa,
                "model": model, "model_fa": model_fa,
                "trim": trim, "trim_fa": trim_fa,
                "family": brand if brand in FAMILY_IS_BRAND else f"{brand}-{model}",
                **to_row(parsed),
                "bama_url": url,
                "aliases": {"bama": ["-".join(p for p in [brand, model, trim] if p)]},
            }
            row["fuel_type"] = fuel_type(trim, trim_fa, name_fa)
            out.append(row)
        return out
