# Spec: Torob for Cars

Status: draft, awaiting user review
Map: [map.md](map.md) · Glossary: [CONTEXT.md](../../CONTEXT.md)

## 1. Product in one paragraph

Buying a used car in Iran means scrolling Divar and Bama, reading messy ads, seeing the same car posted twice, and never knowing whether a price is fair. Torob for Cars lets a buyer **describe what they need in plain Persian**, turns that into visible, editable chips, and returns a ranked list of real Offers from several Sources, merged across sites. Every Offer carries a **deal verdict** measured against similar cars, and the top pick comes with an **explanation written by an LLM from the ranking numbers**, not from its imagination.

**Point of view:** the LLM does what rules are bad at (understanding Persian text, matching messy trim names, writing explanations). Everything that decides the ranking is a plain formula anyone can check by hand. That split is the pitch.

## 2. Scope

| In | Out |
|---|---|
| Used cars, **Tehran only** | Other cities, new-car and dealer prices |
| About 10 models (see §4) | All makes |
| Sources: **Divar** and **Bama** | Sheypoor, Karnameh, Hamrah-e Mechanic |
| One frozen snapshot of about 4–5k Listings | Live crawling during the demo, scheduled re-crawls |
| Persian right-to-left UI | English UI, user accounts, alerts, saved searches |
| Demo video, 5 minutes max | Public hosting |

**Why Tehran only:** the map allowed 1–2 cities, but one city doubles the Offers per comparable group, which is what the verdict needs, and the city Constraint becomes a fixed default.
**Why no Sheypoor:** Divar plus Bama already give enough volume and two naming schemes to reconcile. A third Source adds crawling work without a new idea to show.

## 3. Pipeline

```
crawl ─► normalize ─► dedup ─► market stats ─► search (parse Intent ─► filter ─► rank ─► explain)
 raw      Listing→      Listings   fair price,     per request
 JSON     Vehicle       →Offers    verdict,
                                   Popularity,
                                   Depreciation
```

Offline steps run once to build the snapshot. Search runs on every request. LLM calls are marked **[LLM]**; everything else is deterministic code.

## 4. Data gathering (crawl)

- **Access:** a one-off, private, non-commercial snapshot fetched from the public JSON endpoints that the Sources' own web apps use: Divar's `api.divar.ir/v8/postlist/w/search`, and Bama's listing JSON. **No login, no phone numbers, no captcha bypass.** One request every 2 seconds or slower, stopping at about 3k Divar and 1.5k Bama Listings. The raw response is stored untouched for every Listing.
  - *Why:* the brief explicitly asks to "crawl offers", the volume is tiny, and nothing is republished commercially. Divar's official partner API (Kenar) is the proper production route; the video says so.
  - ⚠️ **Assumption for you to accept:** both Sources' terms forbid automated copying. This spec assumes a small private demo snapshot is acceptable to you. If not, the fallback is to apply for Kenar (Divar only) and drop Bama.
- **Models in scope** (the most-listed in Tehran according to the research): Peugeot 206, Peugeot 207i, Peugeot 405, Peugeot Pars, Pride (111/131/132), Tiba, Dena, Samand, Quick, Shahin. Exact trims come from the catalog.
- **Model-query quirks** (from research): on Bama use `206ir`, because `peugeot,206` silently returns every car, and ignore Bama's total count, which is fake.

## 5. Vehicle catalog

- **Seed JSON** with stable IDs for about 90 trims of the in-scope models, filled once by a script from Bama's make → model → trim tree and spec pages, then **reviewed by hand**.
- **Stored per trim:** make, model, trim, production years, body type, engine size, gearbox, fuel type (taken from the trim name), combined fuel consumption, airbag count, ABS/ESC.
- **Alias table:** (Source, raw name) → trim ID. Bama slugs map directly. Divar aliases start from a sample of posts and grow through normalization (§6).
- *Why hand-curated:* 90 rows is half a day of checking, and a wrong trim silently corrupts every fair price built on it.

## 6. Normalization (Listing → structured record tied to a Vehicle)

1. **Rule-based parsing:** price, year, mileage, gearbox and fuel come from each Source's structured fields. Persian and Arabic digits become Latin; "میلیون" (million) and "میلیارد" (billion) are expanded; everything is stored in **toman**. The solar-calendar model year (for example 1399) is stored as is.
2. **Vehicle match:**
   1. Exact alias lookup.
   2. If none: **[LLM]** receives the raw title, the Source's own category path and the list of catalog trims for that make, and returns `{trim_id | null, reason}`.
   3. The answer is cached per (Source, raw name) and written to the alias table, marked `llm`, for review. So each distinct raw name costs one LLM call, not one per Listing.
3. **Body condition** is mapped to three classes: **clean** (no paint), **minor** (1–2 painted spots or panels), **major** (more paint, accident history or chassis damage). The Source's structured field is used when present; otherwise **[LLM]** reads the description.
4. **Exclusion flags:** instalment or leasing (قسطی / لیزینگی), pre-sale or allocation permit (حواله / پیش‌فروش), and placeholder prices (under 50M toman, or "contact me"). Keywords are checked first, and **[LLM]** confirms using the description.
5. **Unmatched Listings** (no trim) are kept in the database but never shown or used as comparables.

*Why the LLM is here:* trim names differ across Sources in five ways (depth, slugs, mixed attributes, digits and zero-width non-joiners, trims only one Source has). Rules for all of that would be brittle, while choosing from a closed list is a job an LLM does reliably and that can be checked.

## 7. Dedup (Listings → Offers)

Two Listings are **the same car** when they share **trim + model year + body-condition class**, their **mileage differs by at most 1,000 km**, and their **price differs by at most 3%**. This applies within one Source (reposts) and across Sources.

- Merged into one Offer: the Offer **price is the lowest** among its Listings, the attributes come from the most complete Listing (Bama first, because its trim data is structured), and the Offer links to every Listing ("روی ۲ سایت", on 2 sites).
- *Why these signals:* phone numbers need a login and images would need downloading, both out of scope. Sellers usually type the same mileage when cross-posting, so exact trim, year and mileage is a strong fingerprint. The price tolerance covers small edits between posts.
- *Assumption:* two different cars with the same trim and year and mileage within 1,000 km, both in Tehran, are rare enough to ignore.

## 8. Market statistics (per Offer and per Vehicle model)

Comparables are **Offers**, never Listings, so a car posted on two sites isn't counted twice. Offers with an exclusion flag are neither given a verdict nor used as comparables.

### Fair price

**Fair price = median asking price of the comparables.** Comparables are searched in widening tiers, stopping at the first tier with **at least 5** Offers:

| Tier | Same | Model year | Mileage | Confidence |
|---|---|---|---|---|
| 1 | trim, body-condition class | exact | ±20k km | high |
| 2 | trim | ±1 | ±40k km | medium |
| 3 | model (any trim) | ±1 | ±40k km | low |
| — | fewer than 5 at tier 3 | | | no verdict ("داده کافی نیست", not enough data) |

Before taking the median, comparables outside **1.5 × IQR** of their group are removed. The UI says "قیمت منصفانه = میانه قیمت آگهی‌های مشابه" ("fair price = median asking price of similar ads"): it is an asking price, not a sale price, because asking prices are all we can see.

### Verdict

`p` = the share of comparables priced **higher** than this Offer.

| Verdict | Rule |
|---|---|
| ⚠️ **مشکوک** (suspicious) | price more than 25% below the fair price (this check runs first) |
| 🟢 **زیر قیمت** (great deal) | p ≥ 0.8 |
| ⚪ **منصفانه** (fair) | 0.2 < p < 0.8 |
| 🔴 **گران** (overpriced) | p ≤ 0.2 |

*Why percentiles:* they adapt to how spread out each group's prices are. *Why "suspicious":* in this market, a price far below the rest usually means a scam, hidden damage or a fake ad.

**Worked example:** Peugeot 206 Tip 2, model year 1399, 85k km, clean, 495M. Tier 1 finds 11 comparables with a median of 520M, and 9 of the 11 are pricier, so p = 0.82 → 🟢 great deal, high confidence. The UI says "۲۵م زیر میانهٔ ۱۱ خودروی مشابه" (25M below the median of 11 similar cars).

### Popularity and Depreciation (per model)

- **Popularity** = the model's number of Offers, turned into a percentile among the in-scope models.
- **Depreciation** = the average % price drop per year: a straight line fitted through log(median price at each model year) against age.
  - Example: a slope of −0.083 means "about 8% cheaper per year".
  - It needs at least 3 model years with 5 or more Offers each; otherwise it's shown as unknown.

## 9. Intent

Full detail is in [Intent model](issues/03-intent-model.md). In short:

- Free text → **[LLM]** returns JSON validated against a fixed Intent schema. Each chip keeps the words it came from. Numbers are parsed by our code. A keyword and regex fallback runs if the LLM is unavailable.
- **Constraints:** budget, city (Tehran by default) and anything marked "فقط" (only), "حتماً" (definitely) or "نه" (not). Named models are a Constraint; "مثل X" (like X) is a Preference.
- **Preferences** have two levels, **normal** and **strong**.
- **Five Needs:** family, economical, city driving, ride-hailing, holds its value. Each has a fixed recipe of Preferences. What the buyer says explicitly beats a Need's recipe.
- New text replaces the Intent; editing chips adjusts it. Missing fields mean no Constraint. Vague words become Preferences, never invented numbers.

## 10. Ranking

1. **Filter** by Constraints.
   - Offers priced between the budget and 110% of it go to a separate "کمی بالاتر از بودجه" (slightly over budget) group, ranked the same way.
   - Offers marked unmatched are dropped, as §6 says. Excluded ones (instalment and the like) stay visible but get no verdict and are never the top pick.
2. **Score each Preference** from 0 to 1 against the **candidate set**, meaning the Offers that passed the filter:
   - **Numeric** (price, mileage, model year, fuel consumption, airbags, Popularity, Depreciation): the percentile rank within the candidates, in the preferred direction.
   - **Match or no match** (body type, gearbox, fuel, ABS/ESC): 1 or 0.
   - **Body condition:** clean 1, minor 0.5, major 0.
   - **"Like X":** 1 if the same body type and a fair price within ±20% of X's median, otherwise 0.
3. **Deal score** = the verdict's `p`. No verdict → 0.5 (neutral). Suspicious → 0, and the Offer can **never be the top pick**; it shows a warning.
4. **Total score** = (2 · deal + Σ wᵢ · sᵢ) / (2 + Σ wᵢ), where w = 1 for normal and 2 for strong.
   - The deal score always weighs 2, because value for money matters to every buyer; it is the product's point of view.
   - With no Preferences at all, the ranking is simply "best deals first".
5. **Tie-break:** higher verdict confidence, then the newest post.
6. Each Offer's **score breakdown** (every sᵢ, wᵢ and the deal score) is returned by the API and feeds both the UI and the explanation.

**Worked example:** the Intent is "family car up to 800M, very low fuel use". The Preferences are family's sedan body (strong, w = 2), more airbags (1), ABS (1), newer (1), cleaner body (1), and low fuel use (strong, explicit, w = 2). Offer A is a Dena, model year 1400, clean, great deal (p = 0.85), with low fuel use at the 70th percentile. It scores:

(2 · 0.85 + 2 · 1 + 1 · 0.6 + 1 · 1 + 1 · 0.7 + 1 · 1 + 2 · 0.7) / (2 + 8) = **0.84**

Anyone can recompute that from the breakdown shown in the UI.

## 11. Explanation

- **Top pick: [LLM] writes 3–5 Persian sentences** from a **fact sheet** JSON containing:
  - the Intent chips;
  - the top Offer's attributes and verdict (p, comparables count, median, confidence);
  - its three biggest score contributors;
  - for places 2 and 3, the Preference where each lost the most against the top pick.
- **Grounding check:** every number in the LLM's text (after normalizing digits) must appear in the fact sheet, and every Offer it mentions must be one of the three. If the check fails, we use the **template explanation** built from the same fact sheet.
- **Every other Offer** gets a one-line reason from the template, with no LLM, for example "۱۸٪ کم‌مصرف‌تر، ۱۵م زیر قیمت" (18% more fuel-efficient, 15M below fair price).
- *Why:* the explanation is the most visible use of the LLM, and the fact sheet plus the check means it can't claim anything the numbers don't support.

## 12. UI (Nuxt, Persian right-to-left, Vazirmatn font, Persian digits)

1. **Home:** one large search box with a Persian example placeholder, four example-search buttons and five Need shortcuts.
2. **Results:**
   - **Chip bar:** editable chips. Need chips open to show their recipe, and each item can be switched off. Dropped items appear crossed out. There is an empty "بودجه؟" (budget?) chip when no budget was given.
   - **Top pick card:** photo, Vehicle, year, mileage, price, verdict badge, the LLM explanation, and "چرا بقیه نه؟" (why not the others?).
   - **Ranked list:** each card shows the verdict badge (hover shows "ارزان‌تر از ۸۲٪ مشابه‌ها", cheaper than 82% of similar cars), a "روی ۲ سایت" badge when merged, and the one-line reason.
   - The **"slightly over budget"** group follows the main list.
   - **Zero results:** relaxation suggestions with counts, one tap each.
3. **Offer detail:**
   - specs;
   - **price position strip**: comparables as dots, the median marked, this Offer highlighted;
   - score breakdown bars;
   - links to every source Listing.

## 13. Architecture

- **Docker Compose:** `db` (Postgres 16), `api` (Django 5 + Django REST Framework), `web` (Nuxt 3 + Tailwind).
- **Django apps:**
  - `catalog`: Vehicle, VehicleAlias, seed loader.
  - `ingest`: one crawler per Source, RawListing (JSON).
  - `market`: Listing (normalized), Offer, OfferStats, VehicleStats.
  - `search`: Intent parsing, ranking, explanation.
  - `llm`: one client wrapper, the prompts, and a response cache keyed by the prompt's hash.
- **Management commands:** `crawl <source>`, `normalize`, `dedup`, `compute_market`, and `build_snapshot` (all four in order).
  - A snapshot is exported and imported as a fixture, so the demo machine never has to crawl.
- **API:**

  | Endpoint | Input | Output |
  |---|---|---|
  | `POST /api/intent/parse` | `{text}` | Intent |
  | `POST /api/search` | `{intent}` | main and over-budget groups, each with score breakdowns, or relaxation suggestions |
  | `POST /api/explain` | `{intent, offer_ids[3]}` | explanation text and whether the template fallback was used |
  | `GET /api/offers/{id}` | | Offer detail with comparables |
  | `GET /api/needs` | | the Need recipes |

- **LLM:** Claude through the Anthropic API.
  - `claude-haiku-4-5` handles Intent parsing and normalization (cheap and fast, simple structured output).
  - `claude-sonnet-5` writes the explanation (better Persian prose).
  - Every call goes through the `llm` module, so the provider can be swapped.
  - The cache makes demo runs repeatable and cheap.
  - ⚠️ **Assumption:** you can reach the Anthropic API from where you develop and record. If not, the module swaps to another provider.

## 14. Evaluation (enough to trust the demo)

- **Trim matching:** hand-check 40 random normalized Listings. Target ≥ 90% correct; fix aliases if below.
- **Intent parsing:** 12 example sentences with the expected chips, as an automated test.
- **Verdicts:** eyeball 10 Offers (2 per verdict, plus 2 without one) and check their comparables make sense.
- **Grounding:** count how often the explanation falls back to the template over 20 searches. Target ≤ 10%.

## 15. Demo video (5:00 max)

| Time | Beat |
|---|---|
| 0:00–0:30 | The problem: the same 206 on Divar and Bama, messy ads, "is 495M a good price?" |
| 0:30–1:00 | The pipeline on one slide with real counts (Listings crawled → matched → Offers) |
| 1:00–3:15 | Live: type "ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف" (family car up to 800M, very low fuel use) → chips light up with their source words → open the Need chip → top pick and explanation → Offer detail price strip → a ⚠️ suspicious Offer → "اتوماتیک زیر ۳۰۰ میلیون" (automatic under 300M) → relaxation suggestions |
| 3:15–4:30 | Under the hood: the three LLM jobs (Intent, trim matching, explanation) versus the formulas (fair price, verdict, ranking), and the grounding check catching a hallucinated number |
| 4:30–5:00 | Next steps: Kenar API, more cities, sale-price data |

## 16. Open risks

- Sources may change their endpoints or block requests before the snapshot is taken → take the snapshot first, early in the build.
- Too few comparables for rare trims → the tiers fall back, and the demo searches use common models.
- LLM access from Iran → the provider can be swapped (§13).
