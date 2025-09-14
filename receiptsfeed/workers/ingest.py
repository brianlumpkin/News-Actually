import os
import feedparser

def ingest_once(urls):
    for url in urls:
        d = feedparser.parse(url)
        print(f"[ingest] {url}: {len(d.entries)} entries (demo only)")

def main():
    urls = [u.strip() for u in os.getenv("FEED_URLS", "").split(",") if u.strip()]
    if not urls:
        print("[ingest] No FEED_URLS set; nothing to do.")
        return
    print(f"[ingest] Starting… {len(urls)} feeds")
    ingest_once(urls)

if __name__ == "__main__":
    main()
