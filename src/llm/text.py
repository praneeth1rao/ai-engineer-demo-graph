from bs4 import BeautifulSoup
import re

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for x in soup(["script", "style", "noscript"]):
        x.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
