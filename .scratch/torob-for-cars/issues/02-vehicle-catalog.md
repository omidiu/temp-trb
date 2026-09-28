# Vehicle catalog and specs

Type: research
Status: resolved

## Question

Where can we get a canonical Iranian car catalog (make → model → trim, production years) to normalize Listings against, plus the per-trim specs an Intent may care about (body type, seats, engine, gearbox, fuel consumption, safety features)? Candidates: Sources' own brand/model taxonomies (Divar, Bama), manufacturer sites (Iran Khodro, Saipa), spec databases. What's the effort to assemble it for ~10–15 popular models?

## Answer

Findings: branch `research/vehicle-catalog`, file `docs/research/vehicle-catalog.md`.

- **Bama is the best catalog source** (verified): its listing pages expose the full brand → model → trim tree as slugs (e.g. `samand,soren,plusxu7p`), and each trim links to a structured spec page (`/car-reviews/...`) giving engine, displacement, gearbox, combined fuel consumption, body type, airbag count, ABS/ESC and production-year range. It has **no seat count**, and **fuel type** appears only in trim names or on individual ads. Some year ranges conflict and safety changes by year sit in free text, so the data needs a hand review.
- **Divar** uses its own naming with varying depth (e.g. `Samand > Samand Soren > Samand Soren Plus > Samand Soren Plus XU7P Petrol`), present on every post; no full-tree endpoint was found. **Hamrah-e Mechanic** has a third scheme ("206 صندوقدار" = SD).
- Manufacturer sites (ikco.ir, Saipa) were unreachable from outside Iran and would miss discontinued trims anyway. pedal.ir and khodro45 have no structured specs; carvan.ir timed out.
- Trim naming differs in five ways: depth, opaque slugs, mixed axes (engine/gearbox/fuel/options) in the name, Persian vs Latin digits and ZWNJ, and trims that exist on only one Source (e.g. Quick RS only on Divar).

**Recommendation:** our own canonical seed JSON with stable IDs for about 90 trims, filled by a one-off script from Bama's tree and spec pages and then reviewed by hand. Each Source's naming maps through an alias table (source key → canonical ID); Divar aliases are harvested from sampled posts. About 1.5–2 days of work. No live catalog scraper in v1.
