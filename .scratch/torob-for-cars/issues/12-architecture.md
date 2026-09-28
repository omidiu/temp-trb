# Code architecture

Type: grilling
Status: resolved

## Question

How is the code laid out: Django apps, storage, snapshot handling, and the API contract?

## Answer

Decided autonomously (graduated from Not yet specified). Docker Compose (Postgres, Django REST Framework, Nuxt 3); Django apps catalog / ingest / market / search / llm; management commands chained by `build_snapshot`; the snapshot is exported as a fixture; five API endpoints.

Detail: [spec.md](../spec.md) §13.
