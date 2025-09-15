import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlparse
import feedparser
from nlp.heuristics import clickbait_score, ragebait_score, truthiness_score, strip_html

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
  source TEXT,
  clickbait_prob REAL DEFAULT 0,
  ragebait_prob REAL DEFAULT 0,
  score REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
"""

def ensure_columns(cur):
    cur.execute("PRAGMA table_info(articles)")
    cols = {r[1] for r in cur.fetchall()}
    to_add = []
    if "clickbait_prob" not in cols:
        to_add.append("ALTER TABLE articles ADD COLUMN clickbait_prob REAL DEFAULT 0")
    if "ragebait_prob" not in cols:
        to_add.append("ALTER TABLE articles ADD COLUMN ragebait_prob REAL DEFAULT 0")
    if "score" not in cols:
        to_add.append("ALTER TABLE articles ADD COLUMN score REAL DEFAULT 0")
    for stmt in to_add:
        cur.execute(stmt)

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
    ensure_columns(cur)

    total_new = 0

    for feed_url in FEEDS:
        parsed = feedparser.parse(feed_url)
        feed_title = (parsed.feed.get('title') if parsed and getattr(parsed, 'feed', None) else '') or hostname(feed_url)
        new_count = 0
        for e in parsed.entries:
            url = e.get('link') or ''
            title = (e.get('title') or '').strip()
            summary_raw = (e.get('summary') or e.get('subtitle') or '').strip()
            summary = strip_html(summary_raw)
            pub_struct = getattr(e, 'published_parsed', None) or getattr(e, 'updated_parsed', None)
            pub = iso(pub_struct) if pub_struct else datetime.now(timezone.utc).isoformat()

            cb = clickbait_score(title, summary)
            rb = ragebait_score(title, summary)
            sc = truthiness_score(cb, rb)

            try:
                cur.execute(
                    "INSERT OR IGNORE INTO articles(url, title, summary, published_at, source, clickbait_prob, ragebait_prob, score) VALUES(?,?,?,?,?,?,?,?)",
                    (url, title, summary, pub, feed_title, cb, rb, sc)
                )
                if cur.rowcount == 0:
                    cur.execute(
                        "UPDATE articles SET title=?, summary=?, published_at=?, source=?, clickbait_prob=?, ragebait_prob=?, score=? WHERE url=?",
                        (title, summary, pub, feed_title, cb, rb, sc, url)
                    )
                else:
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
