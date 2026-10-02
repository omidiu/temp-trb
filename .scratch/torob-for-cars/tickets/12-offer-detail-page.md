# 12: Offer detail page

**What to build:** Clicking an Offer shows its specs, a price position strip of its comparables with the median, its score breakdown bars, and links to every source Listing.

**Blocked by:** 10

**Status:** done

- [x] `GET /api/offers/{id}` returns detail with comparables
- [x] Price strip, breakdown bars and source links render right-to-left

Spec: [spec.md](../spec.md)

## Notes

- The score breakdown comes from the last search (kept in client state); opening an Offer by direct link shows everything except the breakdown.
