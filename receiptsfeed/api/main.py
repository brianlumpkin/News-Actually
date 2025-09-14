from fastapi import FastAPI
from .routers import feed, articles

app = FastAPI(title="receiptsfeed API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(feed.router, prefix="/feed", tags=["feed"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
