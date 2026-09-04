import requests
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

AI_TERMS = ("ai", "artificial intelligence", "machine learning", "deep learning", "llm", "generative", "nlp", "computer vision", "data scientist", "ml engineer")


def _parse_dt(value):
    if not value:
        return None
    s = str(value).strip()
    # Handle numeric Unix timestamps (seconds or milliseconds)
    try:
        num = float(s)
        # If > 1e12, it's likely milliseconds
        if num > 1e12:
            num = num / 1000.0
        dt = datetime.fromtimestamp(num, tz=timezone.utc)
        return dt
    except (ValueError, OSError):
        pass
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        try:
            dt = parsedate_to_datetime(s)
        except Exception:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _recent(value):
    dt = _parse_dt(value)
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    return now - timedelta(days=7) <= dt <= now + timedelta(hours=1)


def _items(data):
    if isinstance(data, dict):
        for key in ("jobs", "data", "results", "jobPosts"):
            if isinstance(data.get(key), list):
                return data[key]
    return data if isinstance(data, list) else []


def collect_jobs(urls, target=100):
    rows, seen = [], set()
    for url in urls:
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "AI-Engineer-Demo/6.0"})
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"Job source failed: {url} -> {e}")
            continue
        for j in _items(data):
            if not isinstance(j, dict):
                continue
            title = str(j.get("title") or j.get("position") or j.get("name") or "")
            desc = str(j.get("description") or j.get("content") or "")
            if not any(t in f"{title} {desc}".lower() for t in AI_TERMS):
                continue
            date = j.get("pubDate") or j.get("publicationDate") or j.get("date") or j.get("publishedAt") or j.get("created_at")
            if not _recent(date):
                continue
            link = j.get("url") or j.get("applicationLink") or j.get("apply_url") or j.get("guid") or ""
            if not link or link in seen:
                continue
            seen.add(link)
            company = j.get("companyName") or j.get("company") or j.get("company_name") or ""
            remote = j.get("remote")
            remote_label = "Remote" if remote is not False else "Not specified"
            rows.append({"company": company, "date": date, "remote_eligibility": remote_label, "role_family": title, "job_url": link, "source": url})
            if len(rows) >= target:
                return rows
    return rows
