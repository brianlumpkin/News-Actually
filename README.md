# News Actually — Actually news.

Minimal API + SQLite ingest to return a real feed at `/feed`.

## Dev quickstart (Windows / PowerShell)

```powershell
# from the project root
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# create storage folder (if it doesn't exist)
mkdir storage

# ingest a few RSS feeds into SQLite
python scripts/ingest.py

# run the API
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/healthz and http://127.0.0.1:8000/feed

## What’s next
- Add de-dupe, clickbait/rage-bait filters, claim extraction, ClaimReview lookups.
- Replace SQLite with Postgres when you want durability & scale.
