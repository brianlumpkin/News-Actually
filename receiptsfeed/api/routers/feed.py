from fastapi import APIRouter
import os
import feedparser

router = APIRouter()

@router.get("", summary="Return latest feed items (demo)")
def get_feed():
    urls = [u.strip() for u in os.getenv("FEED_URLS", "").split(",") if u.strip()]
    items = []
    for url in urls:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:5]:
                items.append({
                    "title": e.get("title"),
                    "link": e.get("link"),
                    "published": str(e.get("published", "")),
                    "source": url
                })
        except Exception as exc:
            items.append({"error": f"{url}: {exc!r}"})
    return {"items": items[:20]}
