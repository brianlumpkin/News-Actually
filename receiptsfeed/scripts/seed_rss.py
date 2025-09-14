import os, feedparser, json

FEEDS = [u.strip() for u in os.getenv("FEED_URLS", "").split(",") if u.strip()]

def main():
    for url in FEEDS:
        d = feedparser.parse(url)
        print(json.dumps({
            "source": url,
            "count": len(d.entries),
            "sample_titles": [e.get("title") for e in d.entries[:3]],
        }, indent=2))

if __name__ == "__main__":
    main()
