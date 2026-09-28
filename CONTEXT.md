# Torob for Cars

A search and comparison experience for the Iranian used-car market: it gathers ads from many sites, cleans them up, ranks them against what the buyer actually needs, and explains why the top pick is the best choice.

## Language

### Supply

**Source**:
A third-party site whose car ads we gather (e.g. Divar, Bama).
_Avoid_: Provider, vendor, marketplace

**Listing**:
One ad on one Source, as gathered, before any cleanup or merging.
_Avoid_: Ad, post, raw offer

**Vehicle**:
The normalized identity of a car: make, model, trim and production year.
_Avoid_: Car model, spec, variant

**Offer**:
One real car for sale, formed from one or more Listings that describe the same car.
_Avoid_: Listing (when merged), deal, result

### Demand

**Intent**:
What the buyer is looking for, made of Constraints, Preferences and Needs; ranking is measured against it.
_Avoid_: Query, filters, search

**Constraint**:
A hard part of an Intent: an Offer that violates it is excluded (e.g. city, maximum budget, "automatic only").
_Avoid_: Filter, requirement

**Preference**:
A soft part of an Intent: it raises or lowers an Offer's score but never excludes it (e.g. low fuel use, lower mileage).
_Avoid_: Weight, wish

**Need**:
A named buyer situation from a fixed list (e.g. family, economical, ride-hailing) that expands into a set of Preferences.
_Avoid_: Use case, persona, category

### Market

**Popularity**:
How commonly a Vehicle is offered in the market, measured from the Listings we hold.
_Avoid_: Demand, liquidity

**Depreciation**:
How fast a Vehicle's typical price falls as it ages, measured from the Listings we hold.
_Avoid_: Value loss, resale value
