from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path('storage/news.db')

app = FastAPI(title="News Actually API", version="0.0.2")

@app.get('/healthz')
def healthz():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get('/feed')
def feed(limit: int = 25):
    if not DB_PATH.exists():
        return JSONResponse({"items": [], "note": "No DB yet. Run: python scripts/ingest.py"})
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT title, url, summary, published_at, source FROM articles ORDER BY published_at DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    items = [
        {"title": r[0], "url": r[1], "summary": r[2], "published_at": r[3], "source": r[4]}
        for r in rows
    ]
    return {"items": items}
