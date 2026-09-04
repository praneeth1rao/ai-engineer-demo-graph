import re
import requests
from urllib.parse import urljoin

INDEX = "https://webclaw.io/data/startups/llms.txt"
CATEGORIES = [
    "ai", "b2b", "artificial-intelligence", "developer-tools", "productivity", "saas",
    "marketing", "fintech", "consumer", "other", "healthcare", "design-tools",
    "education", "content-creation", "analytics", "open-source"
]
HEADERS = {"User-Agent": "AI-Engineer-Demo/6.0 educational pipeline"}


def _parse_markdown(text, category, source_url):
    rows = []
    lines = (text or "").splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line[1:].strip()
        # Extract URL in parentheses at end of name/website part
        # Match either markdown link - [Name](URL) or plain - Name (URL)
        url = ""
        # Try markdown link format: [Name](URL)
        m_md = re.match(r"\[([^\]]+)\]\((https?://[^)]+)\)", line)
        if m_md:
            name = m_md.group(1).strip()
            url = m_md.group(2).strip()
            rest = line[m_md.end():].strip()
        else:
            # Try plain format: Name (URL)
            m_plain = re.match(r"(.+?)\s*\((https?://[^)]+)\)", line)
            if m_plain:
                name = m_plain.group(1).strip()
                url = m_plain.group(2).strip()
                rest = line[m_plain.end():].strip()
            else:
                continue
        # Extract tagline after em-dash or hyphen
        tagline = re.sub(r"^\s*[—-]\s*", "", rest).strip()
        if not name or not url:
            continue
        # Skip category listing entries (URLs ending in llms.txt)
        if url.rstrip("/").endswith("llms.txt"):
            continue
        rows.append({
            "name": name,
            "website": url,
            "description": tagline,
            "category": category,
            "source_url": source_url,
            "source": "Webclaw Startup Dataset",
        })
    return rows


def _get(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def collect_startups(target=1000):
    rows, seen = [], set()
    urls = [INDEX] + [f"https://webclaw.io/data/startups/{c}/llms.txt" for c in CATEGORIES]
    for url in urls:
        try:
            text = _get(url)
        except Exception as e:
            print(f"Startup source failed: {url} -> {e}")
            continue
        category = "all" if url == INDEX else url.split("/startups/")[1].split("/")[0]
        for row in _parse_markdown(text, category, url):
            key = row["website"].lower().rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
            if len(rows) >= target:
                return rows
    return rows
