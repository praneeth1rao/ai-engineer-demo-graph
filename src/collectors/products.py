import re
import requests
from src.collectors.startups import CATEGORIES, HEADERS, _parse_markdown, INDEX

PRODUCT_TERMS = (
    "ai", "software", "platform", "tool", "api", "agent", "saas", "app",
    "automation", "developer", "copilot", "assistant", "analytics", "search",
    "workflow", "model", "video", "voice", "data"
)


def collect_products(target=1000):
    rows, seen = [], set()
    urls = [INDEX] + [f"https://webclaw.io/data/startups/{c}/llms.txt" for c in CATEGORIES]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            text = r.text
        except Exception as e:
            print(f"Product source failed: {url} -> {e}")
            continue
        category = "all" if url == INDEX else url.split("/startups/")[1].split("/")[0]
        for item in _parse_markdown(text, category, url):
            blob = f"{item['name']} {item['description']} {item['category']}".lower()
            if not any(t in blob for t in PRODUCT_TERMS):
                continue
            key = item["website"].lower().rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "name": item["name"],
                "description": item["description"],
                "website": item["website"],
                "category": item["category"],
                "source_url": item["source_url"],
                "source": "Webclaw public startup/product listing",
                "record_note": "Product candidate derived from the listed company offering; source is retained for traceability.",
            })
            if len(rows) >= target:
                return rows
    return rows
