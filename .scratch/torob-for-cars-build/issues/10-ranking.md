# 10: Ranking

**What to build:** Results are ordered by how well each Offer fits the Intent, with an over-budget group and a per-Offer score breakdown and one-line reason.

**Blocked by:** 07, 09

**Status:** ready-for-agent

- [ ] Constraints filter; Offers up to 110% of budget go to a separate group
- [ ] Preference scores 0–1 (percentile within candidates, or match/no match); total = (2·deal + Σw·s)/(2+Σw), w = 1 normal, 2 strong
- [ ] Deal score = p; no verdict = 0.5; suspicious = 0 and never top pick
- [ ] Tie-break by confidence then newest post
- [ ] Score breakdown in API; template one-line reason on each card; test reproduces the spec's worked example

Spec: [spec.md](../../torob-for-cars/spec.md)
