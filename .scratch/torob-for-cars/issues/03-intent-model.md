# Intent model

Type: grilling
Status: resolved

## Question

What exactly is an Intent? Which fields does it hold (budget, location, use case, year/mileage bounds, body type, gearbox, fuel, brand preferences…), which are hard constraints versus soft preferences with weights, how free text like 'family car under 800M toman, low fuel use, Tehran' maps onto it, and what happens when text is ambiguous or missing fields.

## Answer

### Shape

An **Intent** is a set of **Constraints** (hard: they exclude Offers), **Preferences** (soft: they only affect score, at level `normal` or `strong`), and **Needs** (named situations that expand into Preferences).

| Field | As Constraint | As Preference |
|---|---|---|
| Price (toman) | ≤ max (and/or ≥ min) | lower |
| City | equals | — |
| Model year | ≥ / ≤ | newer |
| Mileage | ≤ | lower |
| Make / model | only these / not these | "like X" → similar class and price |
| Gearbox | only automatic / manual | automatic (via Need) |
| Fuel | only dual-fuel | dual-fuel (via Need) |
| Body type | — | sedan / SUV / hatchback |
| Body condition | e.g. no paint, no accident | cleaner |
| Fuel consumption | — | lower |
| Safety | — | more airbags, has ABS/ESC |
| Popularity | — | higher |
| Depreciation | — | lower |

### Rules

1. **Entry**: free text is parsed into visible, editable chips; the buyer can delete, edit or add chips. New free text replaces the whole Intent; chip edits adjust it. No chat memory.
2. **Hard vs soft**: budget, city, and anything marked with "فقط" (only), "حتماً" (definitely) or "نه" (not) are Constraints; everything else is a Preference. The budget ceiling is hard, but Offers up to 10% over appear in a separate "slightly over budget" group.
3. **Named models** ("۲۰۶ یا کوییک") are a Constraint; with a comparison word ("مثل ۲۰۶", like a 206) they become a "similar to" Preference.
4. **Strength**: intensifiers ("خیلی" very, "حتماً" definitely) or a tap on the chip make a Preference `strong`. Ranking decides what the levels weigh.
5. **Missing fields** mean no Constraint; never block and never ask a follow-up. City defaults to Tehran as a removable chip; an empty "بودجه؟" (budget?) chip nudges.
6. **Vague words** ("ارزون" cheap, "کم‌کارکرد" low mileage) become Preferences, never invented numbers. Only numbers the buyer typed become Constraints.
7. **Zero results**: relax one Constraint at a time and offer the smallest relaxations that bring results back, with counts, one tap each.
8. **Parsing**: the LLM returns JSON validated against a fixed Intent schema, each item carrying the words it came from (so its chip can highlight the phrase). Numbers ("۸۰۰م", "یک و نیم میلیارد") are parsed by our code. If the LLM is unreachable, a keyword/regex fallback extracts price, city, models and Need keywords.

### Needs (MVP)

| Need | Preferences it adds |
|---|---|
| خانوادگی (family) | sedan/crossover/SUV body (**strong**), more airbags, has ABS/ESC, newer, cleaner body |
| اقتصادی/کم‌مصرف (economical) | lower fuel consumption (**strong**), dual-fuel, lower price, higher Popularity |
| شهری (city driving) | hatchback or smaller engine, automatic, lower fuel consumption |
| تاکسی اینترنتی (ride-hailing) | dual-fuel (**strong**), lower fuel consumption, lower mileage, higher Popularity, sedan |
| حفظ ارزش (holds its value) | lower Depreciation (**strong**), higher Popularity, cleaner body, newer |

- Combining Needs: union of their Preferences; a duplicate counts once at the stronger level; opposing Preferences both stay, and ranking balances them.
- Explicit beats derived: a Need's Preference that contradicts an explicit Constraint or Preference is dropped and shown crossed out.
- A Need chip opens to show its recipe; each item can be switched off.

### Worked example

"ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف، فقط اتوماتیک" ("family car up to 800M, very low fuel use, automatic only") →
- Constraints: price ≤ 800,000,000 toman; gearbox = automatic; city = Tehran (default chip)
- Preferences: lower fuel consumption (**strong**, explicit, from "خیلی کم‌مصرف")
- Needs: family → sedan/crossover/SUV body (strong), more airbags, ABS/ESC, newer, cleaner body
- Offers between 800M and 880M appear under "slightly over budget".
