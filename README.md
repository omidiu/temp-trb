# ترب خودرو — Torob for Cars

Search the Iranian used-car market by describing what you need. See `.scratch/torob-for-cars/spec.md` for the spec and `CONTEXT.md` for the vocabulary.

## Run locally

Needs Python 3.14 with `uv`, Node 22+, and Postgres (14+).

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

Or with Docker: `docker compose up --build`.

Tests: `cd backend && uv run pytest`.
