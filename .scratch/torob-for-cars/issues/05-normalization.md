# Normalization pipeline

Type: grilling
Status: resolved
Blocked by: 01, 02

## Question

How does a raw Listing become a normalized record tied to a Vehicle? Which fields are extracted, which by rules (price/mileage/number parsing, Persian digits, toman vs rial) and which by LLM, how a Listing is matched to a Vehicle, how confidence is expressed, and what happens to Listings that can't be normalized.

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). Rules parse numbers and units into toman; trim matching goes alias table first, then an LLM picks from a closed list of the make's catalog trims, cached per raw name and written back as an alias; body condition goes into three classes (clean / minor / major); keyword + LLM exclusion flags; unmatched Listings are kept but never shown.

Full rules, reasons and worked examples: [spec.md](../spec.md) §6.
