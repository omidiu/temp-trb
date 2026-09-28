# 01: Walking skeleton

**What to build:** A buyer opens a Persian right-to-left page, enters a budget, and sees a list of a few hand-made Offers filtered by that budget Constraint, served by Django REST Framework from Postgres. Docker Compose describes db, api and web.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Docker Compose file with db (Postgres 16), api (Django + DRF) and web (Nuxt 3)
- [ ] `POST /api/search` returns Offers filtered by a max-price Constraint
- [ ] Nuxt results page renders right-to-left with Vazirmatn and Persian digits
- [ ] A test covers the budget filter

Spec: [spec.md](../../torob-for-cars/spec.md)
