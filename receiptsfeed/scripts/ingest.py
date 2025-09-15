import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlparse
import feedparser


DB_PATH = 'storage/news.db'


FEEDS = [
'http://feeds.bbci.co.uk/news/rss.xml',
'https://www.theguardian.com/world/rss',
'https://feeds.npr.org/1001/rss.xml',
'https://www.aljazeera.com/xml/rss/all.xml',
]


SQL_CREATE = """
CREATE TABLE IF NOT EXISTS articles (
id INTEGER PRIMARY KEY AUTOINCREMENT,
url TEXT UNIQUE,
title TEXT,
summary TEXT,
published_at TEXT,
source TEXT
);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
"""


def iso(dt_struct):
    try:
        return datetime(*dt_struct[:6], tzinfo=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def hostname(u):
    try:
        return urlparse(u).hostname or ''
    except Exception:
        return ''


def ingest():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for stmt in SQL_CREATE.split(';'):
        if stmt.strip():
            cur.execute(stmt)
    total_new = 0


    for feed_url in FEEDS:
        parsed = feedparser.parse(feed_url)
        feed_title = (parsed.feed.get('title') if parsed and parsed.get('feed') else '') or hostname(feed_url)
        new_count = 0
        for e in parsed.entries:
            url = e.get('link') or ''
            title = (e.get('title') or '').strip()
            summary = (e.get('summary') or e.get('subtitle') or '').strip()
            pub = iso(getattr(e, 'published_parsed', None) or getattr(e, 'updated_parsed', None) or datetime.now(timezone.utc).timetuple())
            try:
                cur.execute(
                   "INSERT OR IGNORE INTO articles(url, title, summary, published_at, source) VALUES(?,?,?,?,?)",
                   (url, title, summary, pub, feed_title)
                )
                if cur.rowcount > 0:
                    new_count += 1
            except Exception as ex:
                print(f"[SKIP] {url} – {ex}")
    total_new += new_count
    print(f"{feed_title}: +{new_count} new")


    conn.commit()
    conn.close()
    print(f"Done. Inserted {total_new} new items.")


if __name__ == '__main__':
    ingest()