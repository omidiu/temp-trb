# 03: Divar crawl and rule normalization

**What to build:** Real Divar Listings for Tehran appear in search results after running the crawl and normalization commands.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] `crawl divar` fetches in-scope models for Tehran at ≤1 request/2s, no login, stores raw JSON per Listing, stops at a configurable cap (default about 3k)
- [ ] Rule normalization: Persian/Arabic digits, million/billion, toman; year, mileage, gearbox, fuel
- [ ] Exact alias match to a Vehicle; body condition mapped to clean/minor/major from structured fields; keyword exclusion flags
- [ ] Unmatched Listings are kept but not searchable
- [ ] Tests for number parsing and condition mapping

Spec: [spec.md](../../torob-for-cars/spec.md)
