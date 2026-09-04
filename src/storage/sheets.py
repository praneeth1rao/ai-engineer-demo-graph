from pathlib import Path
import csv

def write_google_sheet_ready(out_dir, datasets):
    """Writes one CSV per required tab; these can be imported into a Google Sheet.
    Optional direct Sheets integration is intentionally separated from collection.
    """
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    for tab, rows in datasets.items():
        path = out / f"{tab}.csv"
        keys=[]
        for r in rows:
            for k in r:
                if k not in keys: keys.append(k)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            if not keys:
                continue
            w=csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
