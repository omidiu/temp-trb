# 06: Dedup into Offers

**What to build:** A car posted on both Divar and Bama (or reposted) appears once in results at its lowest price, with a 'روی ۲ سایت' (on 2 sites) badge and links to each Listing.

**Blocked by:** 04, 05

**Status:** ready-for-agent

- [ ] Same trim + model year + condition class, mileage within 1,000 km and price within 3% merge into one Offer
- [ ] Offer price is the lowest; attributes come from the most complete Listing (Bama first)
- [ ] `dedup` command rebuilds Offers idempotently
- [ ] Tests for merge and non-merge cases

Spec: [spec.md](../../torob-for-cars/spec.md)
