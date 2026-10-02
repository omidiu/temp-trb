# Used-car search for Tehran

Search the Iranian used-car market by describing what you need in plain Persian. The app gathers ads from Divar and Bama, merges duplicates across sites, says whether each price is a good deal compared with similar cars, ranks the results against your request, and explains why the top pick is the best one.

The LLM does what rules are bad at: understanding Persian text, matching messy trim names, and writing the explanation. Everything that decides the ranking is a plain formula you can check by hand.

## What it does

- **Free-text search.** "ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف" (family car up to 800M, very low fuel use) becomes editable chips: Constraints (budget, gearbox, models), Preferences (low fuel use, newer, cleaner body) and Needs (family, economical, city driving, ride-hailing, holds its value).
- **Merged Offers.** The same car posted on both sites, or reposted, shows up once with a "روی ۲ سایت" (on 2 sites) badge.
- **Deal verdict.** Each Offer is compared with similar Offers (same trim, year and mileage range, widening when there are too few). The fair price is their median asking price. The verdict is great deal, fair, overpriced, or suspicious when the price is far below the rest.
- **Transparent ranking.** Each Offer gets a score from its deal verdict and how well it matches each Preference. The full breakdown is shown on the Offer page.
- **Grounded explanation.** The top pick's explanation is written by Claude from a fact sheet of numbers. If the text mentions a number that isn't in the fact sheet, a template explanation is used instead.
- **Zero results** come with relaxation suggestions (for example, raise the budget), each showing how many Offers it would return.

Scope: Tehran only, about 10 popular models (Peugeot 206/207/405/Pars, Pride, Tiba, Dena, Samand, Quick, Shahin), one frozen snapshot of a few thousand ads.

See `CONTEXT.md` for the vocabulary (Source, Listing, Vehicle, Offer, Intent, …) and the spec under `.scratch/` for the full design.

## Layout

| Path | What |
|---|---|
| `backend/` | Django 5 + Django REST Framework API |
| `backend/catalog/` | Vehicle catalog (hand-reviewed seed JSON) and the Source name → trim alias table |
| `backend/ingest/` | One crawler per Source, raw Listings stored as JSON |
| `backend/market/` | Normalization, dedup, market stats (fair price, verdict, Popularity, Depreciation), snapshot import and export |
| `backend/search/` | Intent parsing, ranking, explanation, and the HTTP API |
| `backend/llm/` | The only door to the LLM, with a response cache |
| `web/` | Nuxt 3 front end, Persian right-to-left |
| `docs/` | Research notes |

## Run locally

Needs Python 3.14 with `uv`, Node 22+, and Postgres 14+.

```sh
# API (defaults to postgres://trb@localhost:5433/trb; override with DATABASE_URL)
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py load_sample_offers   # tiny hand-made dataset
uv run python manage.py runserver 8000

# Web
cd web
npm install
npm run dev    # http://localhost:3000
```

Or with Docker: `docker compose up --build` (Postgres on port 5433, API on 8000, web on 3000).

## Data pipeline

The pipeline runs offline once and produces a snapshot, so the demo machine never has to crawl.

```
crawl ─► normalize ─► dedup ─► market stats ─► search (parse Intent ─► filter ─► rank ─► explain)
```

```sh
cd backend
uv run python manage.py build_snapshot                # load catalog, crawl Bama + Divar (slow: ~2 s per Divar post), normalize, dedup, stats
uv run python manage.py build_snapshot --skip-crawl   # re-run everything after the crawl
uv run python manage.py export_snapshot               # → backend/snapshots/snapshot.json.gz (not in git)
uv run python manage.py import_snapshot               # on the demo machine: no crawling needed
```

The steps can also be run one by one: `load_catalog`, `crawl <bama|divar> [--cap N] [--model NAME]`, `normalize [--no-llm]`, `dedup`, `compute_market`. `build_snapshot` accepts `--divar-cap`, `--bama-cap` and `--no-llm`.

Snapshots contain third-party ad text and are kept out of git.

## LLM

Set `ANTHROPIC_API_KEY` to enable the LLM steps: trim matching, reading body condition from descriptions, Intent parsing, and the top-pick explanation. Without it, rules, aliases and templates are used. Every call is cached by a hash of its prompt, so repeated runs are cheap and give the same answers.

## API

| Endpoint | Input | Output |
|---|---|---|
| `POST /api/intent/parse` | `{text}` | Intent |
| `POST /api/search` | `{intent}` | main and slightly-over-budget groups with score breakdowns, or relaxation suggestions |
| `POST /api/explain` | `{intent, offer_ids}` | explanation text and whether the template fallback was used |
| `GET /api/offers/{id}` | | Offer detail with comparables |
| `GET /api/needs` | | the Need recipes |

## Tests

```sh
cd backend && uv run pytest
```
