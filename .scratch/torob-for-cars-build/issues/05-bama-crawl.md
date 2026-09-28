# 05: Bama crawl

**What to build:** Bama Listings for Tehran appear in search results alongside Divar ones.

**Blocked by:** 03

**Status:** done

- [x] `crawl bama` fetches in-scope models for Tehran at ≤1 request/2s, stores raw JSON, cap about 1.5k
- [x] Handles the `206ir` model-key quirk and ignores Bama's fake total count
- [x] Bama Listings go through the same normalization

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- One search request returns 30 full ads (trim slug, body status, description), so no detail requests. 1,400 raw ads in about 60 requests; ads outside Tehran city are kept but not searchable.
- Some trim IDs from the bootstrap carried a second numeric page ID; `review_fixes.py` strips it so IDs match Bama's ad slugs. A slug with one extra variant segment falls back to its parent trim.
