import csv
import html as _html
import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so src.* imports work on Vercel.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = Path(os.environ.get("DATA_DIR", (ROOT / "data" / "processed").as_posix()))
GITHUB_REPO_URL = "https://github.com/praneeth1rao/ai-engineer-demo-graph"


def _read_csv(path: Path) -> list[dict]:
    """Read a UTF-8-BOM CSV into a list of dicts. Returns [] on any failure."""
    if not path.is_file():
        return []
    try:
        import csv as _csv

        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(_csv.DictReader(f))
    except Exception:
        return []


def _count(path: Path) -> int:
    """Return row count for a CSV file, or 0 if missing/unreadable."""
    return len(_read_csv(path))


def _status_for(entity_rows: list[dict]) -> dict:
    matched = sum(1 for r in entity_rows if str(r.get("status", "")).lower() == "matched")
    unmatched = sum(1 for r in entity_rows if str(r.get("status", "")).lower() == "unmatched")
    total = matched + unmatched
    if total == 0:
        return {"matched": 0, "unmatched": 0, "resolution_rate": None, "total": 0}
    return {
        "matched": matched,
        "unmatched": unmatched,
        "resolution_rate": round(matched / total, 4),
        "total": total,
    }


def _row(label, value, italic=False):
    cls = ' class="muted"' if italic else ''
    return f"<tr><td class='lbl'>{_html.escape(str(label))}</td><td{cls}>{_html.escape(str(value))}</td></tr>"


def _stats_block(title, rows):
    body = "\n".join(_row(k, v) for k, v in rows)
    return f"""
    <div class="card">
      <h3>{_html.escape(title)}</h3>
      <table>{body}</table>
    </div>"""


def build_html() -> str:
    startups = _count(DATA_DIR / "startups.csv")
    products = _count(DATA_DIR / "products.csv")
    papers = _count(DATA_DIR / "research_papers.csv")
    news = _count(DATA_DIR / "news.csv")
    jobs = _count(DATA_DIR / "jobs.csv")
    entity_rows = _read_csv(DATA_DIR / "entity_mapping_log.csv")
    es = _status_for(entity_rows)

    stats_rows = [
        ("Startups", startups),
        ("Products", products),
        ("Research Papers", papers),
        ("Fresh News", news),
        ("Fresh Jobs", jobs),
        ("Entity Mapping Records", es["total"]),
    ]

    entity_rows_html = [
        ("Total entities resolved", es["total"]),
        ("Matched entities", es["matched"]),
        ("Unmatched entities", es["unmatched"]),
        ("Resolution rate", f"{es['resolution_rate']:.2%}" if es["resolution_rate"] is not None else "N/A"),
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Intelligence Graph - AI Engineer Demo</title>
<style>
  :root {{ --bg:#0b1020; --card:#141b2d; --border:#212841; --text:#e6edf7; --muted:#9aa7c0; --accent:#6ee7b7; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif; background:radial-gradient(1200px 600px at 50% -10%, #141b2d 0%, var(--bg) 60%); color:var(--text); min-height:100vh; padding:32px 20px; }}
  .wrap {{ max-width:760px; margin:0 auto; }}
  header {{ margin-bottom:28px; }}
  h1 {{ font-size:22px; margin:0 0 6px; letter-spacing:-0.01em; }}
  .subtitle {{ color:var(--muted); margin:0 0 22px; font-size:14px; }}
  .status-pill {{ display:inline-block; background:#0e2a1f; color:var(--accent); border:1px solid #1f4d3a; padding:4px 10px; border-radius:999px; font-size:12px; margin-bottom:18px; font-weight:600; letter-spacing:0.02em; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
  @media (max-width:560px) {{ .grid {{ grid-template-columns:1fr; }} }}
  .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }}
  .card h3 {{ margin:0 0 10px; font-size:13px; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted); }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:5px 0; border-bottom:1px solid #1a2236; font-size:14px; }}
  td.lbl {{ color:var(--muted); width:60%; }}
  td:not(.muted) {{ font-weight:600; }}
  td.muted {{ color:var(--muted); font-style:italic; }}
  .foot {{ margin-top:28px; text-align:center; color:var(--muted); font-size:12px; }}
  .foot a {{ color:var(--accent); text-decoration:none; }}
  .foot a:hover {{ text-decoration:underline; }}
  .counts {{ font-variant-numeric:tabular-nums; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>AI Intelligence Graph — AI Engineer Demo</h1>
    <p class="subtitle">Project status dashboard · counts read from committed CSV artifacts</p>
    <span class="status-pill">Operational</span>
  </header>

  <div class="grid">
    {_stats_block("Data Statistics", stats_rows)}
    {_stats_block("Entity Resolution", entity_rows_html)}
  </div>

  <div class="foot">
    Source: <a href="{GITHUB_REPO_URL}" target="_blank" rel="noopener">{GITHUB_REPO_URL}</a>
  </div>
</div>
</body>
</html>"""


def handler(request):
    """Vercel serverless function entry point.

    Returns an HTML dashboard for GET/HEAD requests. Counts are read from the
    existing CSV/XLSX artifacts already committed to the repository. No
    data-collection pipeline is executed per request.
    """
    if request.method in ("GET", "HEAD"):
        body = build_html()
        status = 200 if request.method == "GET" else 200
        return {
            "statusCode": status,
            "headers": {
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "public, max-age=60, s-maxage=120",
            },
            "body": body,
        }

    return {
        "statusCode": 405,
        "headers": {"Content-Type": "text/plain; charset=utf-8"},
        "body": "Method not allowed",
    }
