import calendar
import feedparser
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


def _entry_datetime(e):
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = e.get(key)
        if val:
            return datetime.fromtimestamp(calendar.timegm(val), tz=timezone.utc)
    for key in ("published", "updated", "created"):
        val = e.get(key)
        if val:
            try:
                dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _recent(dt):
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    return now - timedelta(days=7) <= dt <= now + timedelta(hours=1)


def _full_text(link):
    try:
        r = requests.get(link, timeout=15, headers={"User-Agent": "AI-Engineer-Demo/6.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for x in soup(["script", "style", "noscript", "svg"]):
            x.decompose()
        return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))[:20000]
    except Exception:
        return ""


def collect_news(feeds, target=100):
    rows, seen = [], set()
    for feed_url in feeds:
        try:
            r = requests.get(feed_url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            r.raise_for_status()
            feed = feedparser.parse(r.text)
        except Exception as e:
            print(f"News feed fetch failed: {feed_url} -> {e}")
            continue
        if getattr(feed, "bozo", 0) and not feed.entries:
            print(f"News feed parse failed: {feed_url}")
            continue
        for e in feed.entries:
            dt = _entry_datetime(e)
            if not _recent(dt):
                continue
            link = e.get("link", "")
            if not link or link in seen:
                continue
            seen.add(link)
            rows.append({
                "title": e.get("title", ""),
                "source": feed_url,
                "date": dt.isoformat(),
                "url": link,
                "full_text": _full_text(link),
            })
            if len(rows) >= target:
                return rows
    return rows
