import sqlite3
from nlp.heuristics import clickbait_score, ragebait_score, truthiness_score, strip_html

DB_PATH = 'storage/news.db'

def reclassify():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(articles)")
    cols = {r[1] for r in cur.fetchall()}
    if "clickbait_prob" not in cols: cur.execute("ALTER TABLE articles ADD COLUMN clickbait_prob REAL DEFAULT 0")
    if "ragebait_prob" not in cols: cur.execute("ALTER TABLE articles ADD COLUMN ragebait_prob REAL DEFAULT 0")
    if "score" not in cols: cur.execute("ALTER TABLE articles ADD COLUMN score REAL DEFAULT 0")

    cur.execute("SELECT id, title, summary FROM articles")
    rows = cur.fetchall()
    updated = 0
    for _id, title, summary in rows:
        title = title or ""
        summary = strip_html(summary or "")
        cb = clickbait_score(title, summary)
        rb = ragebait_score(title, summary)
        sc = truthiness_score(cb, rb)
        cur.execute("UPDATE articles SET clickbait_prob=?, ragebait_prob=?, score=? WHERE id=?", (cb, rb, sc, _id))
        updated += 1

    conn.commit()
    conn.close()
    print(f"Reclassified {updated} rows.")

if __name__ == '__main__':
    reclassify()
