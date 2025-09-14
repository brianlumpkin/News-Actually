from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="News Actually API", version="0.0.1")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/feed")
def feed():
    return {"items": []}
