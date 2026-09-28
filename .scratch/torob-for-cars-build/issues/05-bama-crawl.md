# 05: Bama crawl

**What to build:** Bama Listings for Tehran appear in search results alongside Divar ones.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] `crawl bama` fetches in-scope models for Tehran at ≤1 request/2s, stores raw JSON, cap about 1.5k
- [ ] Handles the `206ir` model-key quirk and ignores Bama's fake total count
- [ ] Bama Listings go through the same normalization

Spec: [spec.md](../../torob-for-cars/spec.md)
