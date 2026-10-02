# 02: Vehicle catalog seed

**What to build:** Results show real Vehicle names and specs from a hand-checkable catalog of about 90 trims of the in-scope models, built once from Bama's tree and spec pages, with Bama aliases.

**Blocked by:** 01

**Status:** done

- [x] One-off script fetches Bama's make/model/trim tree and spec pages for the in-scope models (rate-limited)
- [x] Seed JSON with stable trim IDs and specs (body type, engine size, gearbox, fuel type, fuel consumption, airbags, ABS/ESC, production years), committed for review
- [x] Loader command populates Vehicle and VehicleAlias
- [x] Results display Vehicle make/model/trim

Spec: [spec.md](../spec.md)

## Notes

- `bootstrap_catalog` fetched 94 trims from Bama's spec pages (the filter tree is no longer embedded in listing pages, so trims come from each model's spec page links). `catalog/review_fixes.py` records the hand-review edits: blank gearboxes inferred from trim names, and Pride 132 added from Pride 131 specs (missing from Bama's index). 100 trims total.
- Divar aliases are added in ticket 03 once real Divar model names are known.
