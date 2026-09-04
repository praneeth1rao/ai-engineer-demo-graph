import os, re, requests

API = "https://api.github.com/repos/"


def repo_from_url(url):
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", url or "")
    return f"{m.group(1)}/{m.group(2).removesuffix('.git')}" if m else ""


def enrich_papers(papers):
    token = os.getenv("GITHUB_TOKEN", "").strip()
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-Engineer-Demo/6.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for row in papers:
        repo = repo_from_url(row.get("github_url", ""))
        if not repo:
            continue
        try:
            r = requests.get(API + repo, headers=headers, timeout=15)
            if r.status_code == 200:
                row["github_stars"] = r.json().get("stargazers_count", 0)
                row["github_checked_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        except requests.RequestException:
            continue
    return papers
