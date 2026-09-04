import feedparser
import requests
import time
from urllib.parse import quote

BASE = "https://export.arxiv.org/api/query"
HEADERS = {"User-Agent": "AI-Engineer-Demo/4.0 educational pipeline"}

def collect_papers(target=1000):
    queries = [
        "cat:cs.AI",
        "cat:cs.LG",
        "cat:cs.CL",
        "all:\"large language model\"",
        "all:\"generative AI\"",
    ]
    rows, seen = [], set()

    for search_query in queries:
        start = 0
        while len(rows) < target and start < 3000:
            params = {
                "search_query": search_query,
                "start": start,
                "max_results": 100,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
            try:
                r = requests.get(BASE, params=params, headers=HEADERS, timeout=30)
                r.raise_for_status()
                feed = feedparser.parse(r.text)
            except requests.RequestException as e:
                print(f"arXiv page failed: {e}")
                break

            if not feed.entries:
                break

            for e in feed.entries:
                url = e.get("id", "")
                if not url or url in seen:
                    continue
                seen.add(url)
                authors = "; ".join(a.get("name","") for a in e.get("authors", []))
                rows.append({
                    "title": e.get("title","").replace("\n"," ").strip(),
                    "authors": authors,
                    "paper_url": url,
                    "github_url": "",
                    "github_stars": "",
                    "published_date": e.get("published",""),
                    "source_url": url,
                    "source": "arXiv",
                })
                if len(rows) >= target:
                    break

            start += 100
            time.sleep(0.3)

    return rows[:target]
