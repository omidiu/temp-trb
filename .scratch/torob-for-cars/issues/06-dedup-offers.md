# Dedup Listings into Offers

Type: grilling
Status: resolved
Blocked by: 01

## Question

When do two Listings (on the same or different Sources) describe the same car and merge into one Offer? Which signals (phone, images, text similarity, Vehicle + mileage + price + city), how they combine, the merge threshold, and which Listing's data wins inside an Offer.

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). Same trim + model year + condition class, mileage within 1,000 km, price within 3% → one Offer, within and across Sources. The Offer's price is the lowest of its Listings; attributes come from the most complete Listing (Bama first). No phone or image signals (out of scope).

Full rules, reasons and worked examples: [spec.md](../spec.md) §7.
