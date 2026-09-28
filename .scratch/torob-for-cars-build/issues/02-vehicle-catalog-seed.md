# 02: Vehicle catalog seed

**What to build:** Results show real Vehicle names and specs from a hand-checkable catalog of about 90 trims of the in-scope models, built once from Bama's tree and spec pages, with Bama aliases.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] One-off script fetches Bama's make/model/trim tree and spec pages for the in-scope models (rate-limited)
- [ ] Seed JSON with stable trim IDs and specs (body type, engine size, gearbox, fuel type, fuel consumption, airbags, ABS/ESC, production years), committed for review
- [ ] Loader command populates Vehicle and VehicleAlias
- [ ] Results display Vehicle make/model/trim

Spec: [spec.md](../../torob-for-cars/spec.md)
