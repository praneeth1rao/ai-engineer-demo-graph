import re
from difflib import SequenceMatcher

def normalize(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())

def resolve(name, seed_records, threshold=0.92):
    n = normalize(name)
    best = None
    score = 0.0
    for rec in seed_records:
        s = SequenceMatcher(None, n, normalize(rec.get("name", ""))).ratio()
        if s > score:
            score, best = s, rec
    if best and score >= threshold:
        return {"canonical_name": best.get("name",""), "match_score": round(score, 4), "status":"matched"}
    return {"canonical_name": name, "match_score": round(score, 4), "status":"unmatched"}
