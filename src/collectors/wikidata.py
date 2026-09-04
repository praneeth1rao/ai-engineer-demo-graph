import time
import requests

HEADERS = {"User-Agent": "AI-Engineer-Demo/4.0 educational pipeline"}

def _query(endpoint, query, retries=2):
    for attempt in range(retries):
        try:
            r = requests.get(endpoint, params={"query": query, "format": "json"},
                             headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.json().get("results", {}).get("bindings", [])
            if r.status_code in (429, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
        except requests.RequestException:
            if attempt == retries - 1:
                return []
            time.sleep(2 ** attempt)
    return []

def collect_entities(endpoint, kind, target=1000):
    # Non-critical enrichment only. V4 never depends on Wikidata to finish.
    qclass = "Q4830453" if kind == "startup" else "Q7397"
    query = f"""
    SELECT ?item ?itemLabel ?website ?desc WHERE {{
      ?item wdt:P31 wd:{qclass}.
      OPTIONAL {{ ?item wdt:P856 ?website. }}
      OPTIONAL {{ ?item schema:description ?desc. FILTER(LANG(?desc)="en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 100
    """
    rows = []
    for b in _query(endpoint, query):
        qid = b.get("item", {}).get("value", "")
        if qid:
            rows.append({
                "name": b.get("itemLabel", {}).get("value", ""),
                "website": b.get("website", {}).get("value", ""),
                "description": b.get("desc", {}).get("value", ""),
                "source_url": qid,
                "source": "Wikidata",
            })
    return rows[:target]
