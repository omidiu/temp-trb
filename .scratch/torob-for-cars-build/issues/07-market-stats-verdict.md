# 07: Market stats and verdict

**What to build:** Every eligible Offer in results shows a verdict badge (great deal / fair / overpriced / suspicious / not enough data) with a tooltip like 'cheaper than 82% of similar cars'.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] Fair price = median of ≥5 comparable Offers found in three widening tiers, after 1.5×IQR outlier removal; tier sets confidence
- [ ] Verdict from p = share of comparables priced higher; suspicious if more than 25% below fair price (checked first)
- [ ] Excluded Offers get no verdict and are not comparables
- [ ] Popularity percentile and Depreciation per model
- [ ] `compute_market` command; tests reproduce the spec's worked example

Spec: [spec.md](../../torob-for-cars/spec.md)
