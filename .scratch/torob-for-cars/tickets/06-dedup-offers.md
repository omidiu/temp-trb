# 06: Dedup into Offers

**What to build:** A car posted on both Divar and Bama (or reposted) appears once in results at its lowest price, with a 'روی ۲ سایت' (on 2 sites) badge and links to each Listing.

**Blocked by:** 04, 05

**Status:** done

- [x] Same trim + model year + condition class, mileage within 1,000 km and price within 3% merge into one Offer
- [x] Offer price is the lowest; attributes come from the most complete Listing (Bama first)
- [x] `dedup` command rebuilds Offers idempotently
- [x] Tests for merge and non-merge cases

Spec: [spec.md](../spec.md)

## Notes

- First full run: 1,167 searchable Listings → 1,065 Offers, 52 merged from 2+ Listings.
