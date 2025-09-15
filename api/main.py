from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

DB_PATH = Path('storage/news.db')

app = FastAPI(title="News Actually API", version="0.1.0")

@app.get('/healthz')
def healthz():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

def _query_feed(limit:int, hide_bait:int, min_score:float, order:str):
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    where = ["1=1"]
    params = []
    if hide_bait:
        where.append("(coalesce(clickbait_prob,0) <= 0.55 AND coalesce(ragebait_prob,0) <= 0.55)")
    if min_score > 0:
        where.append("(coalesce(score,0) >= ?)")
        params.append(min_score)
    order_by = "published_at DESC" if order == "recent" else "score DESC, published_at DESC"
    sql = f"""
        SELECT title, url, summary, published_at, source,
               coalesce(clickbait_prob,0), coalesce(ragebait_prob,0), coalesce(score,0)
        FROM articles
        WHERE {' AND '.join(where)}
        ORDER BY {order_by}
        LIMIT ?
    """
    params.append(limit)
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    items = [
        {
            "title": r[0], "url": r[1], "summary": r[2],
            "published_at": r[3], "source": r[4],
            "clickbait_prob": r[5], "ragebait_prob": r[6], "score": r[7]
        }
        for r in rows
    ]
    return items

@app.get('/feed')
def feed(
    limit: int = Query(25, ge=1, le=200),
    hide_bait: int = Query(0, description="1 to hide high clickbait/ragebait"),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    order: Literal["recent","score"] = Query("recent")
):
    if not DB_PATH.exists():
        return JSONResponse({"items": [], "note": "No DB yet. Run: python -m scripts.ingest"})
    return {"items": _query_feed(limit, hide_bait, min_score, order)}

@app.get('/view', response_class=HTMLResponse)
def view(
    limit: int = 25,
    hide_bait: int = 1,
    min_score: float = 60.0,
    order: Literal["recent","score"] = "score"
):
    if not DB_PATH.exists():
        return HTMLResponse("<h3>No DB yet. Run: <code>python -m scripts.ingest</code></h3>", status_code=200)

    items = _query_feed(limit, hide_bait, min_score, order)
    rows = []
    for it in items:
        badge = f"{it['score']:.0f}"
        bait = f"cb:{it['clickbait_prob']:.2f} rb:{it['ragebait_prob']:.2f}"
        rows.append(f"""
          <li style="margin:12px 0;padding:12px;border:1px solid #e5e7eb;border-radius:10px">
            <div style="font-size:14px;color:#6b7280">{it['published_at']} · {it['source']}</div>
            <a href="{it['url']}" target="_blank" style="font-weight:600;font-size:18px;
               color:#111827;text-decoration:none">{it['title']}</a>
            <div style="margin-top:6px;color:#374151">{it['summary']}</div>
            <div style="margin-top:8px;font-size:12px;color:#6b7280">
              score <b>{badge}</b> · {bait}
            </div>
          </li>
        """)
    html = f"""
      <html><head><meta charset="utf-8"><title>News Actually</title></head>
      <body style="font-family:ui-sans-serif,system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:24px">
        <h1 style="margin:0 0 12px">News Actually</h1>
        <div style="color:#6b7280;margin-bottom:8px">
          hide_bait={hide_bait} · min_score={min_score} · order={order} · limit={limit}
        </div>
        <ol style="list-style:none;padding:0;margin:0">{''.join(rows)}</ol>
      </body></html>
    """
    return HTMLResponse(html)

from typing import Literal
import sqlite3

@app.get('/view', response_class=HTMLResponse)
def view(
    limit: int = 25,
    hide_bait: int = 1,
    min_score: float = 60.0,
    order: Literal["recent","score"] = "score"
):
    if not DB_PATH.exists():
        return HTMLResponse("<h3>No DB yet. Run: <code>python -m scripts.ingest</code></h3>", status_code=200)

    where = ["1=1"]
    params = []
    if hide_bait:
        where.append("(coalesce(clickbait_prob,0) <= 0.55 AND coalesce(ragebait_prob,0) <= 0.55)")
    if min_score > 0:
        where.append("(coalesce(score,0) >= ?)")
        params.append(min_score)

    order_by = "score DESC, published_at DESC" if order == "score" else "published_at DESC"

    sql = f"""
      SELECT title, url, summary, published_at, source,
             coalesce(clickbait_prob,0), coalesce(ragebait_prob,0), coalesce(score,0)
      FROM articles
      WHERE {' AND '.join(where)}
      ORDER BY {order_by}
      LIMIT ?
    """
    params.append(limit)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    items = [
      {"title": r[0], "url": r[1], "summary": r[2], "published_at": r[3], "source": r[4],
       "clickbait_prob": r[5], "ragebait_prob": r[6], "score": r[7]}
      for r in rows
    ]

    def row_html(it):
        return f"""
        <li style="margin:12px 0;padding:12px;border:1px solid #e5e7eb;border-radius:10px">
          <div style="font-size:12px;color:#6b7280">{it['published_at']} · {it['source']}</div>
          <a href="{it['url']}" target="_blank" style="font-weight:600;font-size:18px;color:#111827;text-decoration:none">{it['title']}</a>
          <div style="margin-top:6px;color:#374151">{it['summary']}</div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280">
            score <b>{it['score']:.0f}</b> · cb:{it['clickbait_prob']:.2f} rb:{it['ragebait_prob']:.2f}
          </div>
        </li>"""

    body = "".join(row_html(it) for it in items)
    return HTMLResponse(f"""
      <html><head><meta charset="utf-8"><title>News Actually</title></head>
      <body style="font-family:ui-sans-serif,system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:24px">
        <h1 style="margin:0 0 12px">News Actually</h1>
        <div style="color:#6b7280;margin-bottom:8px">
          hide_bait={hide_bait} · min_score={min_score} · order={order} · limit={limit}
        </div>
        <ol style="list-style:none;padding:0;margin:0">{body}</ol>
      </body></html>
    """)

