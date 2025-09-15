# News Actually — Actually news.

SQLite-backed MVP with RSS ingest → bait filters → a scored feed.

## Run it (Windows / PowerShell)

```powershell
# from project root
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir storage -Force

# ingest (creates/updates storage/news.db)
python scripts/ingest.py

# optional: reclassify existing rows after code updates
python scripts/reclassify.py

# run API
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Try these endpoints

- http://127.0.0.1:8000/healthz
- http://127.0.0.1:8000/feed
- http://127.0.0.1:8000/feed?hide_bait=1&min_score=60&order=score
