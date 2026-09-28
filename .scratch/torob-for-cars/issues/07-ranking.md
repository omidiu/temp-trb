# Ranking formula

Type: grilling
Status: resolved
Blocked by: 03, 04

## Question

Given an Intent and a set of Offers, how is the ranked list produced? Define how hard constraints filter, how soft-preference fit and deal verdict combine into one score (weights, normalization), tie-breaking, and how the formula stays explainable. Include worked examples.

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). Filter by Constraints (a separate over-budget group up to +10%); each Preference is scored 0–1 (percentile within the candidates, or match/no match); total = (2·deal + Σ w·s)/(2 + Σ w) with w = 1 normal, 2 strong; suspicious Offers are never the top pick; tie-break on confidence, then the newest post; the score breakdown is returned.

Full rules, reasons and worked examples: [spec.md](../spec.md) §10.
