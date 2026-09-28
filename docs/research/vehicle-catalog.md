# Research: Canonical Iranian vehicle catalog + per-trim specs

Status: research note (2026-09-27). Question: where do we get a canonical
make → model → trim (+ production years) catalog to normalize Listings against,
plus per-trim buyer-relevant specs (body type, seats, engine, gearbox, fuel type,
fuel consumption, airbags/ABS), for the ~10–15 most-listed used models?

All probes below were run on 2026-09-27 from a non-Iranian IP with plain
`curl`/`urllib` (a few dozen requests total, no auth). Quoted values are what the
endpoints returned that day.

## TL;DR

- **Bama is the best single source for both the taxonomy and the specs.** Its
  listing-filter tree is a clean 3-level `brand,model,trim` slug hierarchy
  (187 brands / 1,837 models / 1,352 trims), and every trim links to a
  structured spec page (`/car-reviews/...`) with engine, gearbox, displacement,
  combined consumption, body type, airbag count, ABS/ESC flags and the trim's
  production-year range.
- **Divar has its own, differently shaped taxonomy** (English-string
  hierarchy of variable depth, e.g. `Samand > Samand Soren > Samand Soren Plus >
  Samand Soren Plus XU7P Petrol`). It is exposed on every post, so matching
  Divar → canonical is a mapping table, not fuzzy text matching.
- **Manufacturer sites are not usable from outside Iran** (ikco.ir returns an
  IP-block page; Saipa domains time out) and would not cover discontinued
  trims anyway.
- **Recommendation:** hand-curate a small seed JSON (our own canonical IDs) for
  the ~12 target models, *bootstrapped by a one-off script* from Bama's filter
  tree + spec pages, then hand-review and add a per-source alias table
  (Bama slug, Divar `brand_model` string, Hamrah-Mechanic type name). Do not
  build a live catalog scraper for v1.

## 1. Sources probed

### 1.1 Bama (bama.ir) — taxonomy: YES, specs: YES (verified)

**Taxonomy.** Any listing page, e.g. `https://bama.ir/car/pride-132`, embeds a
Nuxt payload (`<script id="__NUXT_DATA__">`) with key `car-filter-vehicle`: the
full vehicle filter tree. Nodes carry `type` (`brand`/`model`/`trim`), `value`
(a comma-joined slug path) and Persian `text`/`title`, plus search `keywords`
(Persian misspellings + Latin, e.g. `"آیودی aodi آئودی audi"`).
Counts on 2026-09-27: 187 brands, 1,837 model nodes, 1,352 trim nodes.
The same page resolves the URL to a filter:
`{"vehicle":[{"text":"همه نوع پراید 132","value":"pride,132"}]}`.

Target-model excerpt (value = slug path, text = Persian label):

| Bama model (`brand,model`) | Trims (`slug=label`) |
|---|---|
| `peugeot,206ir` پژو 206 | type1, type2, type3, type3panorama, type4, type5, type6 (`تیپ N`) |
| `peugeot,206sd` پژو 206 SD | v1, v2, v6, v8, v9, v10, v19, v20 |
| `peugeot,405` | gl, gli, glx, glxcng, slx (TU5), slxxu7 |
| `peugeot,pars` | at, cng, elxtu5, elx (ELX-XU7), elxxu7p, elxxum, lx, mt (XU7), xu7p |
| `pride,111` / `131` / `132` / `141` / `151` | ex, le, lx, se, sl, sx, tl, basic (ساده) … varies per model |
| `pride,sedan`, `pride,hatchback`, `pride,station` | (no trims — old "Saba/Nasim" era) |
| `tiba,sedan` | plus, ex, lx, sl, sx (بنزینی), sxcng |
| `tiba,hatchback` | plus, ex, sx |
| `dena,plus` (دنا پلاس EF7) | turbo, basicmanual, turbo6mt, turboautomaticoptional, turboautomatic |
| `dena,plusef7p`, `dena,1.7` (دنا معمولی) | 6mt / none |
| `samand,lx` | ef7, ef7cng, tu5, basic (= XU7) |
| `samand,soren` | plus, pluscng, plustu5p, plusxu7p, basic, elx, elxturbo |
| `samand,se`, `samand,el`, `samand,x7`, `samand,sarir` | (no trims) |
| `quick,…` | models: manual, manualr, manuals, atfull, atfullplus, gx{hmt,lmt}, gxr{hmt,lmt}, manualrplus{at,mt}, sr{mt} |
| `shahin,…` | models: g, gl, s, gautomatic{cvt,cvtgl}, plusat{at6,at6gl} |
| `runna,…` | models: el, lx, plus{tu5,tu5plus}, pluspanorama |

Note the brand level is the *marque as sold* (pride, samand, dena, tiba, quick,
shahin, runna), not the manufacturer (Saipa / Iran Khodro). Bama's price list
does add a `class` field such as `"ایران خودرو"` on some rows.

**Ads.** `GET https://bama.ir/cad/api/search?pageIndex=0` returns JSON ads
with `detail.{title, trim, year, transmission, fuel, body_type_fa, cylinder_fa}`
and `specs.{volume, engine, fuel (consumption), url_price, url_review}` — i.e.
each ad already links to its canonical spec page, e.g.
`/car-reviews/peugeot/206sd-specs-1085-v8`. (The `vehicle=` query parameter was
ignored in my probe — both `peugeot-206` and `peugeot,206` returned the mixed
feed — so the right filter parameter for the API is unverified; the SSR page
`/car/pride-132` does filter.)

**Spec pages.** `https://bama.ir/car-reviews/{brand}/{model}-specs-{id}[-{trim}]`
(brand index: `https://bama.ir/car-reviews/pride`). The page's `window.__NUXT__`
payload has `trims:[{url,trim,trim_fa}]`, `years:[{year:"1385-1400"}]`,
`comparison_code:"1085-v8"`, and `specsData` = sections of
`{key, value, type}` rows where booleans are rendered as check-icons.
~110 keys, including everything the buyer-intent list asks for **except seats
and fuel type**:

- engine `پیشرانه` ("4 سیلندر TU5"), displacement `حجم موتور`, power, torque,
  0–100, top speed
- gearbox `گیربکس` ("5 دنده دستی"), drive `محور محرک`
- combined consumption `مصرف ترکیبی` ("6.6 لیتر در صد کیلومتر")
- body type `نوع بدنه` ("سدان کوچک", "هاچ بک جمع و جور"), dimensions, weight, tank
- airbags `مجموع ایربگ‌ها` + per-position flags; ABS, EBD, BA, ESC, TCS, HSA …
- comfort/multimedia flags; expert score and pros/cons text

Sample extraction (per-trim values as returned):

| Page | Years (field) | Engine | Gearbox | Cons. l/100km | Body | Airbags | ABS | ESC |
|---|---|---|---|---|---|---|---|---|
| peugeot/206ir type2 | 1380–1401 | TU3 1.4 L | 5MT | 6.4 | هاچ بک جمع و جور | 2 | yes | no |
| peugeot/206sd v8 | 1385–1400 | TU5 1.6 L | 5MT | 6.6 | سدان کوچک | 2 | yes | no |
| pride/131 sl | 1389–1391 | M13 Euro3 1.3 L | 5MT | 6.7 | سدان کوچک | 0 | yes | no |
| tiba/sedan sx | 1388–1401 | M15 1.5 L | 5MT | 6.9 | سدان کوچک | 2 | yes | no |
| samand/lx basic (XU7) | 1382–1401 | XU7 1.8 L | 5MT | 8.3 | سدان جمع و جور | 2 | yes | no |
| samand/soren plus (EF7) | 1399–1404 | EF7 1.7 L | 5MT | 7.3 | سدان جمع و جور | 2 | yes | "از پاییز 1402" |
| dena/plus basicmanual | 1396–1402 | EF7 1.7 L | 5MT | 7.9 | سدان جمع و جور | 2 | yes | no |
| quick/manualr | 1398–1402 | M15 Euro4 1.5 L | 5MT | 7.0 | هاچ بک کوچک | 2 | yes | no |
| shahin/g | 1399–1405 | M15T 1.5 L turbo | 5MT | 7.2 | سدان جمع و جور | 2 | yes | "از تابستان 1402" |
| peugeot/405 gli | 1383–1385 | L3 1.8 L | 5MT | 9.0 | سدان جمع و جور | 2 | yes | no |
| peugeot/pars elxxu7p | 1401–1402 | XU7 plus 1.8 L | 5MT | 7.0 | سدان جمع و جور | 2 | yes | no |

**Data-quality caveats observed (why we must hand-review):**
- Year ranges disagree within a page: pride/131 SL field says 1389–1391 but the
  `<title>` says 1389–1399; 405 GLI field 1383–1385 vs title 1370–1401. The
  title range appears to be the *model* span, the field the *trim* span — needs
  checking per row.
- One spec row per trim spans the whole year range; mid-life changes live in
  free text (206 SD: "حذف سنسور، ضبط و ترمز دیسکی عقب (از سال 98)"; ESC on
  Shahin/Soren "from 1402"). A binary ABS/airbag flag per trim can be wrong
  for early years (e.g. ABS=yes on 206 type 2 across 1380–1401 is plausible for
  later years only — **not verified**).
- No explicit seat count (derive: 5 for all target models; 7-seaters appear
  only as trim names elsewhere, e.g. Fidelity `7seater`).
- Fuel type is not a spec key; it is encoded in trim names (`cng`, "دوگانه
  سوز", "بنزینی") and on each ad (`detail.fuel`). Divar also has
  "دوگانه‌سوز دستی" (aftermarket CNG), so fuel is partly a *listing* attribute,
  not purely a trim attribute.

### 1.2 Divar (divar.ir) — taxonomy: YES (per post; full tree not fetched)

- Filter widget `brand_model` is `I_LAZY_MULTI_SELECT_HIERARCHY_ROW` with
  `lazy_payload {filter_name:"brand_model", version:"6ab9510a", category:"light"}`
  and online search key `car_brand_model` (from `window.__PRELOADED_STATE__` on
  `https://divar.ir/s/tehran/car`). The lazy options endpoint was not in the
  loaded JS chunks, so **the full tree was not fetched — unverified**.
- It is not needed: every post detail
  (`GET https://api.divar.ir/v8/posts-v2/web/{token}`) carries its breadcrumb as
  successive `brand_model` values plus Persian rows. Examples observed:

  | Divar hierarchy (English values) | Persian row `برند و مدل` |
  |---|---|
  | Peugeot › Peugeot 206 › Peugeot 206 2 | پژو 206 تیپ ۲ |
  | Pride › Pride 131 › Pride 131 SE | پراید 131 SE |
  | Samand › Samand Soren › Samand Soren Plus › Samand Soren Plus XU7P Petrol | سمند سورن پلاس XU7P بنزینی |
  | Quick › Quick GXR › Quick GXR L | کوییک GXR تیپ L |
  | Quick › Quick Automatic › Quick Automatic Full-plus | کوییک اتوماتیک فول پلاس |
  | Quick › Quick RS | کوییک RS |

  Other leaf values seen in schema.org JSON-LD on the SSR list page:
  `Peugeot 206 5`, `Peugeot Pars Bi-fuel`, `Pride Sedan petrol`,
  `Pride 132 SX`, `Samand LX basic`, `Quick manual R-normal`, `Saipa Sahand S`,
  `Peugeot 207i manual TU5`.
- Post also exposes `مدل (سال تولید)` ("۱۳۸۸ - ۲۰۰۹"), `گیربکس`, `نوع سوخت`.
- Search accepts any hierarchy prefix: `POST https://api.divar.ir/v8/postlist/w/search`
  with `brand_model: ["Peugeot 206"]` returned 206 hatch *and* 206 SD posts
  (titles "پژو 206 SD V8"), so Divar may nest 206 SD under "Peugeot 206" —
  not confirmed on an SD post.

### 1.3 Hamrah-Mechanic (hamrah-mechanic.com) — third taxonomy (verified)

`https://www.hamrah-mechanic.com/carprice/peugeot/` `__NEXT_DATA__` →
`brandPricesList` rows `{brandEnglishName, modelName, modelEnglishName,
carModelId, carTypeName, carTypeId, carYear, marketPrice}`. Naming diverges
again: `پژو 206 صندوقدار` (not "SD"), `پژو 405 SLX` as a *model*, Pars trims
like "LX با دریچه گاز برقی" (throttle type), 207 "دنده ای با موتور ESP - TU3".
Has numeric IDs and per-year rows — useful as a *used-price* source later, not
as the canonical catalog.

### 1.4 Manufacturer sites — not reachable (verified failure)

- `ikco.ir`, `www.ikco.ir`, `ikco.ir/fa`: HTTP 403 with "این سایت با آی پی فعلی
  شما قابل دسترس نمی‌باشد" (geo/IP block).
- `saipacorp.com`, `www.saipacorp.com/portal/`, `saipa.ir`: connection timeout.
- Even from inside Iran they list *current* production only; discontinued
  trims (Pride 111/131/141, 206 type 3/6, Samand LX XU7, 405 GLI) — the bulk
  of the used market — would be missing. Useful only for spot-checking current
  trims, from an Iranian IP. **Not verified.**

### 1.5 Other spec/news sites

- `khodro45.com`: used-car trading + price estimator (`/carprice/`); no spec
  catalog found (WebFetch summary of homepage; not deeply probed).
- `pedal.ir`: car magazine (news, reviews, buying guides); no structured spec
  database found for domestic models (WebFetch summary).
- `carvan.ir`, `khodro70.com`: timed out. **Not verified.**
- Prior art: [sobhanaz/khodrobin](https://github.com/sobhanaz/khodrobin) (MIT,
  created 2026-09-06, 4 stars) — "ترب برای خودروی دست‌دوم", crawls
  Divar/Bama/Hamrah-Mechanic. Its tree has only `data/seed/listings.seed.jsonl`
  and no catalog/alias file, so nothing to reuse for the catalog.

## 2. How trim naming differs (matters for matching)

| Canonical idea | Bama slug / label | Divar value / label | Hamrah-Mechanic |
|---|---|---|---|
| Peugeot 206 hatch, tip 2 | `peugeot,206ir,type2` / پژو 206 تیپ 2 | `Peugeot 206 2` / پژو 206 تیپ ۲ | پژو 206 / تیپ 2 (assumed) |
| Peugeot 206 sedan V8 | `peugeot,206sd,v8` / پژو 206 SD V8 | likely `Peugeot 206 SD V8` (unverified) | پژو 206 صندوقدار / V8 |
| Samand Soren Plus XU7P petrol | `samand,soren,plusxu7p` / سمند سورن پلاس XU7P بنزینی | `Samand Soren Plus XU7P Petrol` (4 levels) | — |
| Samand LX with XU7 | `samand,lx,basic` / سمند LX XU7 | `Samand LX basic` | — |
| Pars bi-fuel | `peugeot,pars,cng` / پژو پارس دوگانه سوز | `Peugeot Pars Bi-fuel` | پژو پارس / … |
| Quick R manual | model `quick,manualr` (no trim) | `Quick manual R-normal` | — |
| Quick RS | *absent* (Bama has `quick,sr`) | `Quick RS` | — |

Patterns:
1. **Depth differs.** Bama is fixed 3 levels; Divar is 2–4 levels; Quick/Shahin
   variants are *models* on Bama but deeper nodes on Divar.
2. **Same slug, different meaning.** Bama `samand,lx,basic` = XU7 engine;
   `peugeot,pars,mt` = "XU7"; `pride,132,basic` = "ساده". Slugs are opaque —
   always use the label, never infer from the slug.
3. **Axes mixed into the trim.** Trim names blend option pack (SE/SX/TL),
   engine (TU5/XU7P/EF7), gearbox (دنده ای/اتوماتیک/6MT), fuel (CNG/بنزینی)
   and roof (پانوراما). Canonical Vehicle should keep `trim` as a label but also
   carry decomposed `engine`, `gearbox`, `fuel` fields so partial matches work.
4. **Script/numerals.** Persian vs Latin digits (تیپ ۲ vs تیپ 2), ZWNJ in
   "دنده‌ای", "تیپ" prefix optional, Latin vs Persian for "SD"/"صندوقدار".
   Normalize digits + ZWNJ before alias lookup.
5. **Coverage gaps both ways** (Quick RS on Divar only; Bama's `pride,station`),
   so the catalog needs an explicit "unknown trim under known model" state.

Because both big Sources expose *structured* trim identifiers on every listing,
matching is mostly an exact lookup in an alias table
`(source, source_vehicle_key) → canonical_vehicle_id`; free-text parsing is only
needed for listings without a trim (or with a model-only value like
`Peugeot 206`).

## 3. Effort estimate for ~12 models

Rough trim count in Bama's tree for the target set (206 hatch, 206 SD, Pride
111/131/132/141, Tiba sedan/hatch, Dena/Dena+, Samand LX/Soren, Quick family,
405, Pars, Shahin, Runna): **~90 trims**.

| Approach | Effort | Notes |
|---|---|---|
| Live scraper that syncs catalog from Bama | 3–5 days + ongoing | Nuxt payload parsing (IIFE-minified vars for spec pages), breakage on redeploys, ToS exposure; overkill for a static domain. |
| **One-off bootstrap script + hand-reviewed seed JSON** | **~1.5–2 days** | ~½ day script (filter tree + ~90 spec pages, rate-limited), ~1 day review: fix year ranges, split trims where ABS/ESC changed by year, add Divar/Hamrah aliases from sampled posts. |
| Pure hand-curation from memory/articles | 2–3 days | Slower and less accurate on consumption/airbag values than copying Bama. |

Divar aliases: sample ~20–50 posts per model via the search + post APIs to
collect distinct `brand_model` leaves (this also reveals which trims actually
matter by volume), then map them by hand.

## 4. Recommendation

1. **Own the canonical catalog as a checked-in seed file** (e.g.
   `data/vehicles.seed.json`) with our own stable IDs:
   `make, model, trim, year_from, year_to, body_type, seats, engine_code,
   displacement_l, gearbox, fuel, consumption_l_100km, airbags, abs, esc,
   notes`, plus `aliases: {bama: "samand,soren,plusxu7p", divar:
   ["Samand Soren Plus XU7P Petrol"], hamrah: [...]}`.
2. **Bootstrap it from Bama** (filter tree for the hierarchy, `/car-reviews`
   pages for specs), run once, then **hand-review** — Bama is the most complete
   structured source, but its year ranges and per-year safety changes need
   correction. Keep the Bama `comparison_code` for traceability.
3. **Model Divar as an alias table, not a second catalog.** Collect leaves from
   real posts; unmapped leaves go to a review queue.
4. Treat **fuel (CNG retrofit), and year-dependent safety kit as Listing-level
   overrides** where the listing says so; the catalog provides defaults.
5. Skip manufacturer sites and third-party magazines for v1; revisit only if
   Bama's spec data proves wrong in review.

## Unverified / open

- Divar's full `brand_model` tree endpoint (lazy filter) — not found.
- Whether Divar nests 206 SD under `Peugeot 206`.
- Correct filter parameter for Bama's `/cad/api/search` JSON API.
- Accuracy of Bama's ABS/airbag flags for early production years.
- Manufacturer sites and carvan.ir/khodro70.com (unreachable from probe IP).
- Terms of use for automated fetching from Bama/Divar (not reviewed).
