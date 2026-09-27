# Source feasibility: where to get Iranian used-car Listings

**Question.** Which 2–3 Sources should "Torob for Cars" crawl for used-car Listings, and how? Candidates: Divar, Bama, Sheypoor, Karnameh, Hamrah-e Mechanic. The demo runs on a frozen snapshot of a few thousand Listings, covering about 10–15 popular models in Tehran (1–2 cities).

**Method.** Probed live on 2026-09-27 (Tehran evening, Sunday) with curl and small Python scripts, about 60 requests in total spread over 5 sites, spaced 2–3 s apart. No bulk crawling. Read robots.txt and ToS pages where they could be found. Anything not observed directly is marked **unverified**.

---

## TL;DR recommendation

| Rank | Source | Access method | Why |
|---|---|---|---|
| 1 | **Divar** | Official **Kenar** `finder/post` search (API key) to seed tokens, plus `finder/post/{token}` for details. Fallback is the unauthenticated web JSON API (`api.divar.ir/v8/postlist/w/search`, `/v8/posts-v2/web/{token}`). | By far the largest volume (hundreds of new Tehran posts per day for each target model) and the richest structured fields. It is the only candidate with a *sanctioned* API. |
| 2 | **Bama** | Unauthenticated JSON `GET bama.ir/cad/api/search?vehicle=…&region=…&pageIndex=N`, plus the detail page's SSR Nuxt payload. | Clean, fully structured JSON with trim, body/paint status, gearbox, fuel and exact `modified_date`. It is the car-specialist complement to Divar. **But its ToS explicitly forbids automated copying** (see Risks). |
| 3 (optional) | **Sheypoor** | Unauthenticated JSON `GET sheypoor.com/api/v10.0.0/search/tehran/car/{brand}`. | Real `total` counts, structured attributes including chassis/body condition, and a third independent price signal. ToS not located. |
| Skip | Karnameh | – | Only **312 listings nationwide**, all concierge sales (`post_type: CS`). Too thin. The company is also tied to Divar (its inspection reports are shown on Divar), so it adds little. |
| Skip | Hamrah-e Mechanic | – | About **2,334 inspected-inventory cars nationwide**. Only 81 Peugeot 206, 35 Pride, 11 Peugeot 405 and 3 Dena. Good data quality, too few Listings. |

For a frozen demo snapshot, **Divar + Bama** already give well over "a few thousand" Listings for the 7 target models in Tehran. Add Sheypoor if the demo needs 3 Sources to show cross-Source comparison.

---

## 1. Divar (divar.ir)

### Access

- **Web SSR.** `GET https://divar.ir/s/tehran/car` returns HTML with `window.__PRELOADED_STATE__` embedded (about 536 KB). It includes the post rows plus schema.org `Car` JSON-LD for each post (brand, model, `productionDate`, `mileageFromOdometer`, `vehicleTransmission`, `color`, `knownVehicleDamages`, `offers.price` in IRR). Observed.
- **Internal web JSON search (no auth).** Observed working:
  ```http
  POST https://api.divar.ir/v8/postlist/w/search
  Content-Type: application/json

  {"city_ids":["1"],
   "search_data":{"form_data":{"data":{
      "category":{"str":{"value":"light"}},
      "brand_model":{"repeated_string":{"value":["Peugeot 206"]}}}}}}
  ```
  - `city_ids: ["1"]` is Tehran. `category: light` is passenger cars and pickups.
  - `brand_model` values were confirmed by the filter working: `"Peugeot 206"`, `"Peugeot 405"`, `"Pride"`, `"Tiba"`, `"Dena"`, `"Samand"`, `"Quick"`. Finer values exist too, e.g. `"Pride 131 SE"`. The response's `SEO_LINKS` widgets list the valid child values.
  - Each page has about 24 `POST_ROW` widgets (26 including promoted ones). Rows carry the title, mileage, price text, a district/"shop" label, the thumbnail and the token.
  - **Pagination is cursor-based.** Echo `pagination.data` back as `pagination_data` in the next request. Verified: page 2 returned 24 new tokens with 0 overlap. **No total count** is returned. Default sort is `sort_date` (bumped/"پله شده" posts re-surface).
- **Post detail (no auth).** `GET https://api.divar.ir/v8/posts-v2/web/{token}` returns a sectioned widget JSON (about 39 KB), verified. `seo.unavailable_after` is about 31 days after posting, so a Listing lives for about 30 days.
- **Phone.** `POST https://api.divar.ir/v8/postcontact/web/contact_info_v2/{token}` returns **401 `LOGIN_REQUIRED`**, verified. Phone numbers need a logged-in account. Don't collect them.
- **Official API, Kenar (Divar open platform).** This is the primary source: [kenar-docs `search_post.md`](https://github.com/divar-ir/kenar-docs/blob/HEAD/docs/post/search_post.md).
  - `POST https://open-api.divar.ir/v2/open-platform/finder/post` takes `x-api-key` and needs the `SEARCH_POST` permission. It filters by `category`, `city`, `districts`, and `query.brand_model` / `production_year` / `usage`.
  - **Hard limit: 100 calls total, even for production apps.** There is no pagination, and each call returns up to **100 newest posts**. The doc explicitly warns against features that rely on it.
  - `GET https://open-api.divar.ir/v1/open-platform/finder/post/{token}` takes an API key only (no OAuth). It returns title, description, images, price, `brand_model`, etc. ([get_post](https://divar-ir.github.io/kenar-docs/post/get_post)).
  - Rate limits are a fixed per-minute limit plus a daily quota, which can be raised on request. Exceeding them returns HTTP 429 ([scopes](https://divar-ir.github.io/kenar-docs/scopes/)). The actual numbers are not published (**unverified**).
  - 100 calls × 100 posts is about **10k tokens max**. That is enough for one frozen demo snapshot (e.g. 7 models × a few district/year slices), then `get_post` per token within the daily quota. Registering a Kenar app is required. **Unverified:** eligibility requirements (Iranian business/phone), approval time, and whether `SEARCH_POST` is granted to new apps.

### Fields (observed on a live Pride 131 post and in JSON-LD)

| Field | Available? | Where |
|---|---|---|
| Price | Yes | `webengage.price` (toman, int). Detail row "قیمت پایه". JSON-LD `offers.price` (IRR). |
| Year | Yes | "مدل (سال تولید)" e.g. `۱۳۹۸ - ۲۰۱۹`. JSON-LD `productionDate`. |
| Mileage | Yes | "کارکرد". JSON-LD `mileageFromOdometer`. |
| Trim | Partly | `brand_model` e.g. `Pride 131 SE`. The trim granularity depends on the seller's choice. |
| City / district | Yes | `city`, `webengage.district` (e.g. `kan`), and the district label. |
| Body/paint condition | Yes (seller-declared) | `SCORE_ROW`s: موتور, شاسی جلو, شاسی عقب, بدنه (e.g. "خط و خش جزیی"), گیربکس. JSON-LD `knownVehicleDamages`. |
| Gearbox | Yes | "گیربکس". |
| Fuel | Yes | "نوع سوخت". |
| Color | Yes | "رنگ". |
| Seller type | Yes | `webengage.business_type` (`personal` vs dealer). The list label "نمایشگاه در …" marks dealers. |
| Phone | **No** (login required) | – |
| Images | Yes | `IMAGE_CAROUSEL` items on `s100.divarcdn.com`. |
| Post date | Approximate | The detail page gives only relative text ("دقایقی پیش"). The list `pagination.last_post_date` has exact bumped timestamps. `unavailable_after` minus 31 days gives the post date. Kenar search returns `last_modified_at`. |
| Insurance | Yes | "مهلت بیمهٔ شخص ثالث". |

### Volume (Tehran, `category=light`)

Divar returns no totals. I measured the time span covered by the first page of 24 posts, sorted by date, at about 18:00–21:30 Tehran time. This includes bumped posts and was taken at evening peak, so treat these as an **upper-bound posting rate**:

| Model | First 24 posts span | ≈ posts/day (peak rate) |
|---|---|---|
| Pride | 0.98 h | ~630 |
| Samand | 1.25 h | ~500 |
| Peugeot 206 | 1.27 h | ~490 |
| Quick | 1.59 h | ~390 |
| Peugeot 405 | 2.53 h | ~250 |
| Dena | 2.57 h | ~240 |
| Tiba | 4.55 h | ~140 |

Even at a quarter of these rates, with Listings living about 30 days, **each model has thousands of active Tehran Listings on Divar**. That is order-of-magnitude reasoning, not a count.

### Anti-bot / rate limits

- Sotoon CDN (`server: Sotoon CDN`, `x-zrk-*` headers). The CSP allows `api.arcaptcha.ir` (a captcha provider) and `ap.api.fpjs.io` (FingerprintJS). The feature flag `device_fp_enable: true` is set in cookies. The site is **clearly equipped** for device fingerprinting and captcha.
- ~12 unauthenticated API calls at 2–3 s spacing all got HTTP 200. No rate-limit headers were returned. I did **not** try to find the throttle threshold.
- **Unverified:** whether non-Iranian IPs are blocked. My probes succeeded from this machine, whose network location I did not check.

### ToS / robots

- robots.txt disallows only `/my-divar/*`, `/new`, `/s/*/*?*q=*` (free-text search) and `/adminbot`. Category/brand listing pages and `/v/` post pages are crawlable per robots.
- ToS: the terms page (`divar.ir/help/custom_articles/general_terms_and_conditions`) is client-rendered and I could not read it directly. A search-engine snippet of `divar.ir/__contact_terms/` (now 404) quotes: *"استفاده‌کننده از دیوار حق کپی‌برداری از اطلاعات آگهی‌دهنده، نوشتار و تصاویر آگهی‌های ارسال شده به دیوار را چه به شکل دستی و یا خودکار نخواهد داشت و انجام این موارد پیگرد قانونی دارد."* In English: users may not copy advertiser info, text or images, manually or automatically, and doing so carries legal liability. **Treat this as the stance (scraping prohibited), but the current wording is unverified.** Kenar is the sanctioned path.

---

## 2. Bama (bama.ir)

### Access

- The site is Nuxt (`x-powered-by: Nuxt`) on Sotoon CDN. List pages SSR a `__NUXT_DATA__` devalue payload that includes the first page of ads and the complete vehicle filter tree.
- **JSON search (no auth).** Verified:
  `GET https://bama.ir/cad/api/search?vehicle=peugeot,206ir&region=tehran&pageIndex=N`
  - `vehicle` is `brand[,model[,trim]]`. Slugs come from the filter tree: `peugeot,206ir` (domestic 206; also `206sd`, `206im`), `peugeot,405`, `pride` (and `pride,131`…), `tiba`, `dena` (also `dena,plus`), `samand` (also `samand,lx`…), `quick`.
    - **Gotcha:** `vehicle=peugeot,206` is silently ignored and returns *all* cars.
  - `region=tehran` limits results to Tehran *province* (~80–85% Tehran city in samples, plus Varamin, Eslamshahr, etc.).
  - 30 ads per page; `pageIndex` is 0-based. `metadata.total_count` is **not a real total**. It grows as you page (rolling "seen + 31"). Detect the end with `ads == []` / `has_next: false`.
  - Ordering is ranking-based, not strictly chronological.
- **Detail.** `https://bama.ir/car/detail-{code}-…` SSR payload key `get-ad-pdp-car_{code}`. It carries the description, structured location `{province, city, region}`, full-size image `original` URLs, and **`phone` masked as `۰۹۱۲۴۷۹۹۸XX`** (the full number presumably needs a click/API; not probed).

### Fields (observed in `/cad/api/search` ad objects)

| Field | Available? | Where |
|---|---|---|
| Price | Yes | `price.type` (`lumpsum` / `negotiable` / installments) and `price.price` (toman string). "negotiable" has price 0. |
| Year | Yes | `detail.year` (Jalali for domestic cars, Gregorian for imports). |
| Mileage | Yes | `detail.mileage` ("250,000 km" / "صفر کیلومتر"). |
| Trim | **Yes, structured** | `detail.trim` and the URL slug (e.g. `peugeot-206ir-type2`). |
| City | Yes | `detail.location` ("تهران / الهیه"). Detail gives `{province, city, region}`. |
| Body/paint condition | **Yes, structured** | `detail.body_status`, e.g. بدون رنگ, خط و خش جزئی, یک/دو/چند لکه رنگ, کاپوت تعویض, کامل رنگ. |
| Gearbox | Yes | `detail.transmission`. |
| Fuel | Yes | `detail.fuel`. |
| Color | Yes | `body_color`, `inside_color`. |
| Body type | Yes | `body_type`, `body_type_fa`. |
| Seller type | Yes | `dealer` object (null means private). |
| Phone | Masked | Detail `content.phone` ends in `XX`. |
| Images | Yes | `images[]` with large/small/thumb, plus `original` on the detail page. |
| Post date | **Yes, exact** | `detail.modified_date` (ISO). `time` is relative text. |
| Specs | Yes | `specs` (engine, volume, fuel economy). |

### Volume (Tehran province, measured by paging to the end with a bounded binary search)

| Model (slug) | Active ads |
|---|---|
| Peugeot 206 (`peugeot,206ir`) | **~880** (29 full pages + 10). Oldest `modified_date` about 2026-08-11. |
| Quick | ~660 |
| Dena | ~600–660 |
| Pride | ~240–300 |
| Samand | ~180–240 |
| Peugeot 405 | ~125 |
| Tiba | **57** |

Low Pride/Tiba numbers compared with Divar suggest Bama skews toward dealers and higher-value cars. **Unverified:** whether some Pride/Tiba ads sit under other slugs (e.g. `saipa,…`).

### Anti-bot / rate limits

- About 20 API calls at 2.5–3 s spacing all returned 200 in about 1 s, with no rate-limit headers. The event API (`/event/api/v1/events`) suggests client telemetry. No captcha was seen. Throttling thresholds are **not tested**.

### ToS / robots

- robots.txt is permissive. It lists sitemaps (`/sitemap/car`, `/sitemap/car-filters`, …) and disallows only campaign banners.
- **The ToS explicitly prohibits scraping.** From [bama.ir/terms](https://bama.ir/terms), verified verbatim:
  - *"استفاده از هرنوع فناوری رایانه ای، جهت مرور یا کپی خودکار صفحات و اطلاعات سایت باما، موجب پیگرد است."* In English: any computer technology used to automatically browse or copy Bama's pages or information is subject to prosecution.
  - *"هر گونه باز نشر یا کپی اطلاعات آگهی از سایت باما بدون اخذ مجوز کتبی از مدیر سایت … موجب پیگرد است … همچنین استخراج اطلاعات تماس آگهی کنندگان … مشمول این بند است."* In English: republishing or copying ad data without written permission is prosecutable, and so is extracting advertisers' contact info.

---

## 3. Sheypoor (sheypoor.com)

### Access

- The HTML embeds `window.__DEHYDRATED__STATE__` and references its own API base `https://www.sheypoor.com/api/v10.0.0`.
- **JSON search (no auth).** Verified: `GET https://www.sheypoor.com/api/v10.0.0/search/tehran/car[/{brand}]`. Brand slugs include `peugeot`, `pride`, `tiba`, `dena`, `samand`, `quick`.
  - `meta.total` and `meta.normal_count` are real totals. There are 24 items per page, mixed with `special`/`vip`/`paidEngagement`/banner items.
  - `meta.f` is a cursor string. **Unverified:** how deep pagination works. `?p=2` and `?p=40` returned near-identical results, so the cursor `f` is probably required.
- Model-level filtering (e.g. 206 vs 207 within `peugeot`) goes through attribute filters (`/api/v10.0.0/search/filters/tehran/car`). Not probed. Filtering client-side on `fullAttributes["مدل خودرو"]` works.

### Fields (observed)

| Field | Available? | Where |
|---|---|---|
| Price | Yes | `attributes.price[].amount` (toman). |
| Year | Yes | fullAttributes "سال تولید (چهار رقمی)". |
| Mileage | Yes (33 of 35 items) | "کیلومتر". |
| Trim | Yes (free-ish) | "مدل خودرو", e.g. `206 (تیپ2)`, `سورن پلاس EF7 بنزینی`. |
| City / district | Yes | `attributes.location` ("تهران، تجریش"). |
| Body/paint condition | **Yes** | "وضعیت بدنه", "وضعیت شاسی جلو", "وضعیت شاسی عقب". |
| Gearbox / Fuel / Color | Yes | "گیربکس", "نوع سوخت", "رنگ". |
| Cash/installment | Yes | "نقدی/اقساطی". |
| Seller type | Partly | `shopLogo` is non-null for shops. |
| Phone | Masked | `telephone: "0915XXX9284"`. |
| Images | Yes | `cdn.sheypoor.com/imgs/YYYY/MM/DD/{id}/…`. |
| Post date | Approximate | `timePassedLabel` is relative. The image path date is a proxy. |

### Volume (Tehran, `meta.total` / `normal_count`)

| Brand | total | normal |
|---|---|---|
| Peugeot (all) | 1,665 | 1,010 |
| Pride | 947 | 451 |
| Samand | 403 | 240 |
| Quick | 305 | 182 |
| Dena | 271 | 183 |
| Tiba | 156 | 81 |

### Anti-bot / ToS

- `server: nginx`, `x-cache: MISS`. About 10 calls returned 200 with no rate-limit headers or captcha.
- robots.txt disallows `/search`, `/*?` (except `page_num=`), `/session`, `/pro`, `/trumpet`. The `/api/…` paths are not mentioned.
- **ToS not found.** The footer "قوانین و مقررات" link points to `/faq`, which is client-rendered and does not contain the terms. `/terms`, `/pages/terms` and `/pages/rules` return 404. **Assume the stance is similar to Divar/Bama (unverified).**

---

## 4. Karnameh (karnameh.com): skip

- Next.js SSR. `https://karnameh.com/buy-used-cars` `__NEXT_DATA__` → `pageProps.firstPage` reports **`total: 312` nationwide** (20 per page). All sampled posts were `post_type: "CS"` (concierge sale) in Tehran.
- Fields: price, year, `usage` (km), brand/model (EN+FA), `gearbox`, city, images, `has_inspection`. No per-post body status in the list.
- The ToS ([/car-inspection/terms](https://karnameh.com/car-inspection/terms)) was verified:
  - *"5-9- هرگونه باز نشر یا کپی محتوای آگهی‌های منتشره از طریق پلتفرم کارنامه، منجر به نقض حقوق کاربران و کارنامه است و کارنامه حق هرگونه اقدام و پیگیری قانونی را خواهد داشت."* In English: any republishing or copying of ad content from Karnameh violates users' and Karnameh's rights, and Karnameh reserves the right to take legal action.
  - Clause 21-4 states that Karnameh inspection reports are shown on Divar. The ToS also names Divar's operating company (آگه‌پردازان هوشمند). These are closely linked platforms, so Karnameh inventory likely overlaps Divar.
- robots.txt disallows `/pictures/car-posts` and `/*?*post_token=*`.

## 5. Hamrah-e Mechanic (hamrah-mechanic.com): skip

- Next.js on ArvanCloud. Note that the TLS chain is incomplete: Python `urllib` failed certificate verification, while curl worked.
- `https://www.hamrah-mechanic.com/cars-for-sale/` `__NEXT_DATA__` → `cars.totalCount: 2334` (24 per page). The model paths `/cars-for-sale/{brand}/{model}/` return per-model totals: Peugeot 206 **81**, Peugeot 405 **11**, Dena **3**, Pride **35**, Saipa (all) 378. Samand at `irankhodro/samand` returned 0 (the slug is probably different; unverified).
- Very high data quality: `km`, `gearBox`, `carTypeName` (trim), `carYear`, color, location, price, and a full `inspectionReport` (بدنه و شاسی, فنی و مکانیکی, …). It exposes a consultant phone (the company's, not the seller's). This is dealer-style inventory, not a classifieds site.
- robots.txt disallows many filter query params (`?brand`, `?model`, `?km`, `?bodycondition`…). The ToS page was not found (`/terms/` is 404). **Unverified.**

---

## Recommendation

1. **Divar (primary, sanctioned route first).**
   - Register a Kenar app. Spend some of the 100 `finder/post` search calls on Tehran × {7 target brand_models} × a few `production_year`/`usage` slices, collecting ≤100 newest tokens per call. Hydrate each token with `finder/post/{token}` under the daily quota.
   - This yields a few thousand Tehran Listings with price, year, mileage, brand_model and images, and it stays inside Divar's rules.
   - If Kenar access is denied or too slow, the unauthenticated `api.divar.ir/v8/postlist/w/search` + `/v8/posts-v2/web/{token}` endpoints work today. However, that is scraping against the (unverified-text) ToS. Keep it to a one-time, low-rate snapshot.
2. **Bama (secondary: best structured fields).** `cad/api/search` with correct slugs plus `region=tehran` gives trim, body_status, gearbox, fuel and an exact date. That is ideal for normalization and for showing cross-Source price comparison. **Only use it after deciding the legal risk is acceptable.** For a private, non-public demo on a frozen snapshot, the exposure is low. For anything public, ask Bama for written permission, which the ToS explicitly offers ("بدون اخذ مجوز کتبی").
3. **Sheypoor (optional third).** Similar field richness with real totals. Include it only if a third Source is needed for the demo narrative.

### Risks

- **Legal/ToS.** Bama and Karnameh explicitly prohibit automated copying (verified). Divar prohibits it per an indexed ToS snippet (current text unverified). Sheypoor and Hamrah-e Mechanic are unknown. Mitigations:
  - Prefer Kenar.
  - Keep the snapshot private and frozen.
  - Store no phone numbers.
  - Link out to the original Listing.
  - Hot-link or cache images only as needed.
- **Anti-bot.** Divar ships FingerprintJS and ArCaptcha hooks. All Sources sit behind Iranian CDNs (Sotoon, Arvan), which can geo-filter. Throttle thresholds were not tested. Keep to ≤1 req / 2–3 s, a single IP and a one-shot run.
- **API drift.** All non-Kenar endpoints are undocumented internals (Divar `v8`, Bama `cad/api`, Sheypoor `v10.0.0`) and can change without notice. Freeze raw JSON responses in the snapshot so the demo never depends on live endpoints.
- **Data quirks.**
  - Divar ordering includes bumped posts, and the detail page has no exact post date.
  - Bama's `total_count` is fake. `vehicle=peugeot,206` silently returns all cars (use `206ir`), and `region=tehran` means the province.
  - Years are Jalali for domestic cars and Gregorian for imports.
  - Prices are in toman (Divar JSON-LD uses IRR). "Negotiable"/0 prices need handling.
  - The same car is often cross-posted on Divar, Bama and Sheypoor, so the demo needs de-duplication (or can show it as a feature).
- **Kenar uncertainty.** Onboarding requirements, approval time, whether the `SEARCH_POST` permission is granted, and the daily quota numbers are all unverified.

## Not verified

- Divar's current ToS wording. Sheypoor's and Hamrah-e Mechanic's ToS.
- Rate-limit thresholds on any Source (deliberately not stress-tested).
- Whether foreign IPs are blocked, since my probe machine's location was not checked.
- Kenar app eligibility, approval time, and daily quota numbers.
- Deep pagination on Sheypoor (the cursor `f` semantics).
- Bama's full phone reveal flow.
- Exact Divar active counts per model (only rate-based estimates).
- The Hamrah-e Mechanic Samand/Dena slugs.

## Sources

- Live probes, 2026-09-27:
  - `divar.ir/s/tehran/car`, `api.divar.ir/v8/postlist/w/search`, `api.divar.ir/v8/posts-v2/web/{token}`, `api.divar.ir/v8/postcontact/web/contact_info_v2/{token}`
  - `bama.ir/car/peugeot-206`, `bama.ir/cad/api/search`, `bama.ir/car/detail-…`, [bama.ir/terms](https://bama.ir/terms)
  - `sheypoor.com/s/tehran/car`, `sheypoor.com/api/v10.0.0/search/…`, [sheypoor.com/faq](https://www.sheypoor.com/faq)
  - `karnameh.com/buy-used-cars`, [karnameh.com/car-inspection/terms](https://karnameh.com/car-inspection/terms), [karnameh.com/privacy](https://karnameh.com/privacy)
  - `hamrah-mechanic.com/cars-for-sale/…`
  - robots.txt of all five sites
- Divar Kenar docs:
  - [search_post.md](https://github.com/divar-ir/kenar-docs/blob/HEAD/docs/post/search_post.md)
  - [get_post](https://divar-ir.github.io/kenar-docs/post/get_post)
  - [scopes / rate limits](https://divar-ir.github.io/kenar-docs/scopes/)
  - [kenar-docs home](https://divar-ir.github.io/kenar-docs/)
- Divar ToS snippet: web search result for [divar.ir/__contact_terms/](https://divar.ir/__contact_terms/) (the page now returns 404).
