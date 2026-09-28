# Source feasibility

Type: research
Status: resolved

## Question

Which 2–3 Sources should we crawl for Iranian used-car Listings (candidates: Divar, Bama, Sheypoor, Karnameh, Hamrah-e Mechanic), and how? For each: how Listings are reachable (public/internal JSON API vs HTML), anti-bot measures and rate limits, terms of service, which fields are available (price, year, mileage, trim, city, body/paint condition, gearbox, fuel, seller type, phone, images, post date), and rough Listing volume for popular models in Tehran.

## Answer

Findings: branch `research/source-feasibility`, file `docs/research/source-feasibility.md` (about 60 light requests on 2026-09-27).

**Recommendation: Divar first, Bama second, Sheypoor optional. Skip Karnameh (312 listings nationwide, tied to Divar) and Hamrah-e Mechanic (about 2.3k inspected cars; 81 Peugeot 206, 3 Dena).**

- **Divar**: by far the most Listings (hundreds of new Tehran posts per day per target model, an upper-bound estimate) and the richest fields: seller-declared body/chassis condition, gearbox, fuel, seller type. Phone needs login. Access:
  - Official partner API "Kenar": search is capped at 100 calls in total × 100 newest posts each (about 10k posts, enough for one snapshot); post details by ID need only an API key. Onboarding is unverified.
  - Fallback: the site's internal JSON API (`api.divar.ir/v8/postlist/w/search`, cursor-paged, no login). The terms (seen via a search-engine cache) ban automated copying.
- **Bama**: clean JSON with structured trim, body/paint status and exact dates. Tehran-province counts: 206 about 880, Quick about 660, Dena about 630, Tiba 57. The terms explicitly ban automated browsing or copying without written permission (verified).
- **Sheypoor**: JSON with real totals (Tehran: Peugeot 1,665, Pride 947, Samand 403) and body/chassis condition. Terms not found.
- **Risks**: the terms of Divar, Bama and Karnameh prohibit scraping; Divar ships fingerprinting and captcha tools; the internal endpoints are undocumented, so raw responses must be stored. Quirks: Bama's total count is fake, and `vehicle=peugeot,206` silently returns every car (use `206ir`). Cross-posting is common, so dedup matters.
- **Not verified**: rate-limit thresholds, whether foreign IPs are blocked, Kenar onboarding.
