# 10: Ranking

**What to build:** Results are ordered by how well each Offer fits the Intent, with an over-budget group and a per-Offer score breakdown and one-line reason.

**Blocked by:** 07, 09

**Status:** done

- [x] Constraints filter; Offers up to 110% of budget go to a separate group
- [x] Preference scores 0–1 (percentile within candidates, or match/no match); total = (2·deal + Σw·s)/(2+Σw), w = 1 normal, 2 strong
- [x] Deal score = p; no verdict = 0.5; suspicious = 0 and never top pick
- [x] Tie-break by confidence then newest post
- [x] Score breakdown in API; template one-line reason on each card; test reproduces the spec's worked example

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- Placeholder-price Offers are never searchable (their price is meaningless for budget filters); instalment/pre-sale Offers stay visible with no verdict and are never the top pick.
- A Preference with unknown data for an Offer (e.g. missing airbag count) scores a neutral 0.5 and is marked `known: false` in the breakdown.
