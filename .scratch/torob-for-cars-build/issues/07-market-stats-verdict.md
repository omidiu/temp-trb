# 07: Market stats and verdict

**What to build:** Every eligible Offer in results shows a verdict badge (great deal / fair / overpriced / suspicious / not enough data) with a tooltip like 'cheaper than 82% of similar cars'.

**Blocked by:** 06

**Status:** done

- [x] Fair price = median of ≥5 comparable Offers found in three widening tiers, after 1.5×IQR outlier removal; tier sets confidence
- [x] Verdict from p = share of comparables priced higher; suspicious if more than 25% below fair price (checked first)
- [x] Excluded Offers get no verdict and are not comparables
- [x] Popularity percentile and Depreciation per model
- [x] `compute_market` command; tests reproduce the spec's worked example

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- First full run over 1,065 Offers: 140 great, 338 fair, 174 overpriced, 14 suspicious, 399 without a verdict (too few comparables or excluded). Depreciation comes out at 4–8% a year for most models (asking prices in toman, so inflation offsets part of the age effect).
