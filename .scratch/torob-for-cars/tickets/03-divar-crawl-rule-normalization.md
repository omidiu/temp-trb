# 03: Divar crawl and rule normalization

**What to build:** Real Divar Listings for Tehran appear in search results after running the crawl and normalization commands.

**Blocked by:** 01, 02

**Status:** done

- [x] `crawl divar` fetches in-scope models for Tehran at ≤1 request/2s, no login, stores raw JSON per Listing, stops at a configurable cap (default about 3k)
- [x] Rule normalization: Persian/Arabic digits, million/billion, toman; year, mileage, gearbox, fuel
- [x] Exact alias match to a Vehicle; body condition mapped to clean/minor/major from structured fields; keyword exclusion flags
- [x] Unmatched Listings are kept but not searchable
- [x] Tests for number parsing and condition mapping

Spec: [spec.md](../spec.md)

## Notes

- Until ticket 06, each searchable Listing (Vehicle + year + mileage + price) becomes its own Offer (`dedup` command).
- Divar aliases live in `catalog/data/divar_aliases.json` (hand-mapped); more are added as the crawl covers more models.
- Crawl rate observed: about 2 s per post (one detail request per post).
