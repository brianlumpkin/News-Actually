# receiptsfeed (starter)

Minimal scaffold matching your layout, with FastAPI + Postgres + demo workers.

## Run with Docker
1. Copy `.env.example` to `.env` and tweak if needed.
2. Start: `docker compose up`
3. API: http://localhost:8000/health and http://localhost:8000/feed
4. Stop: `docker compose down`

## Local dev without Docker
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn receiptsfeed.api.main:app --reload
```

## Next steps
- Wire `articles` router to the DB (see `storage/schema.sql`).
- Flesh out workers (`ingest`, `classify`, `verify`) and call real NLP in `receiptsfeed/nlp/*`.
- Create a Vite app under `receiptsfeed/web` (this repo only includes stubs).
