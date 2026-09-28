# Fair price and deal verdict

Type: grilling
Status: resolved
Blocked by: 01

## Question

How is an Offer's fair price estimated and turned into a verdict (great deal / fair / overpriced)? Define: what counts as a comparable, how year, mileage, trim, city and body condition adjust price, the exact formula, verdict thresholds, the minimum number of comparables, and the fallback when there are too few. Also define how each Vehicle's Popularity and Depreciation are calculated from the snapshot (both are Intent Preferences). Include worked examples.

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). Fair price = median asking price of at least 5 comparable Offers, found in three widening tiers (trim + condition + exact year → trim ±1 year → model ±1 year), with 1.5×IQR outliers removed; the tier gives the confidence. Verdict from p = share of comparables priced higher: great deal p ≥ 0.8, overpriced p ≤ 0.2, suspicious if more than 25% below fair price. Instalment, pre-sale and placeholder prices are excluded. Popularity = percentile of a model's Offer count; Depreciation = slope of log median price against age.

Full rules, reasons and worked examples: [spec.md](../spec.md) §8.
