from pathlib import Path
from openpyxl import Workbook

def write_workbook(path, datasets):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook(); wb.remove(wb.active)
    for tab, rows in datasets.items():
        ws = wb.create_sheet(tab[:31])
        keys=[]
        for r in rows:
            for k in r:
                if k not in keys: keys.append(k)
        if keys: ws.append(keys)
        for r in rows: ws.append([r.get(k, "") for k in keys])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
    wb.save(path)
