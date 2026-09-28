# Torob for Cars

Labels: wayfinder:map

## Destination

A build-ready spec at `.scratch/torob-for-cars/spec.md` for "Torob for Cars" (Iranian used-car market): product scope, domain model, the crawl → normalize → rank → explain pipeline with every piece of logic defined, stack decisions, and the demo-video plan. Done when `/to-tickets` can slice it into build tickets with nothing left to decide.

## Notes

- **Context**: hiring-challenge style brief ("Build Torob for X"), judged mainly on the ≤5 min demo video and a clear point of view. ~1–2 weeks part-time.
- **Point of view**: intent-first search (entry) + deal verdict / fair price (core ranking signal) + cross-Source dedup into Offers (bonus). The user must understand the logic behind each: every grilling ticket ends with the logic written plainly, with formulas and worked examples.
- **Standing decisions**: Persian RTL UI. LLM only at the edges (text → structure: Intent parsing, field extraction; structure → prose: explanation); fair price, verdict and ranking are deterministic, inspectable formulas. Real crawler, demo runs on a frozen snapshot of a few thousand Listings. Scope: ~10–15 most-listed models in 1–2 cities. Stack: Nuxt + Django REST Framework + Postgres, simple scheduled crawl job (no Celery unless needed). Deliverable is the video only; no public hosting.
- **Vocabulary**: use `CONTEXT.md` (Source, Listing, Vehicle, Offer, Intent).
- **Skills**: grilling tickets → `grilling` + `domain-modeling`; research → `research`; prototype → `prototype`.
- **Git**: no Claude co-author trailer on commits.
- **Override (2026-09-28)**: the user asked Claude to decide details autonomously, keep things simple and consistent, give a reason for each choice, and bring only the final spec for review. This overrides one-ticket-per-session and the grilling of HITL tickets.

## Decisions so far

- [Vehicle catalog and specs](issues/02-vehicle-catalog.md): hand-reviewed seed JSON (~90 trims) built once from Bama's tree + spec pages; per-Source alias tables map naming; no seat data, fuel type only from trim names.
- [Source feasibility](issues/01-source-feasibility.md): Divar first (most volume, richest fields), Bama second, Sheypoor optional; skip Karnameh and Hamrah-e Mechanic; Divar and Bama terms prohibit scraping.
- [Intent model](issues/03-intent-model.md): free text → editable chips; Constraints (budget, city, 'only/not') vs Preferences (normal/strong); five Needs with fixed Preference recipes; LLM returns schema-validated JSON, our code parses numbers, keyword fallback.
- [Fair price and deal verdict](issues/04-fair-price-verdict.md): median of ≥5 comparable Offers in widening tiers; percentile verdict plus a 'suspicious' flag; Popularity and Depreciation from the snapshot.
- [Normalization pipeline](issues/05-normalization.md): rules for numbers; alias table, then the LLM picks the trim from a closed list; three condition classes; exclusion flags.
- [Dedup Listings into Offers](issues/06-dedup-offers.md): trim + year + condition + mileage ±1k km + price ±3%; lowest price wins.
- [Ranking formula](issues/07-ranking.md): filter by Constraints, then (2·deal + Σw·s)/(2+Σw) with percentile Preference scores.
- [Explaining the best choice](issues/08-explanation.md): the LLM writes from a fact sheet; a grounding check falls back to a template.
- [UI flow](issues/09-ui-flow.md): Home → Results (chips, top pick, list) → Offer detail (price strip, breakdown).
- [Crawl access and terms of service](issues/10-crawl-access.md): one-off private, rate-limited snapshot of Divar and Bama; Kenar named as the production route. ⚠️ Needs the user's acceptance.
- [LLM provider and access](issues/11-llm-provider.md): Claude (Haiku for extraction, Sonnet for explanations) behind a swappable module and a cache.
- [Code architecture](issues/12-architecture.md): Compose with Postgres, DRF and Nuxt; five Django apps; snapshot as a fixture.
- [Evaluation](issues/13-evaluation.md): small hand checks plus a golden Intent test.
- [Demo video](issues/14-demo-video.md): a five-beat, 5-minute storyline.

## Not yet specified

_Empty: every patch graduated and was resolved. The spec draft is at [spec.md](spec.md), awaiting user review._

## Out of scope

- Public hosting / a live URL for judges: the video is the only deliverable (user decision while charting).
- Nationwide, all-makes coverage and new-car dealer/factory prices: depth on ~10–15 used models beats breadth.
- Second city, Sheypoor, phone- or image-based dedup, user accounts and alerts: they add work without adding to the point of view (decided while writing the spec).
