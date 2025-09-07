from __future__ import annotations
import csv
import io
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Optional

if TYPE_CHECKING:
    from fishki.models import Card

REQUIRED_COLS = ["de","en"]
ALL_COLS = ["de","en","example","tags","notes"]

def read_csv(path: str) -> List[Dict[str, str]]:
    rows = []
    # uploaded file from streamlit is an in-memory file
    if hasattr(path, 'getvalue'):
        csvfile = io.StringIO(path.getvalue().decode('utf-8'))
        r = csv.DictReader(csvfile)
    else:
        f = open(path, "r", encoding="utf-8-sig", newline="")
        r = csv.DictReader(f)

    missing = [c for c in REQUIRED_COLS if c not in r.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {', '.join(missing)}")
    for row in r:
        clean = {k: (row.get(k,"") or "").strip() for k in ALL_COLS}
        if not clean["de"] or not clean["en"]:
            continue # Skip empty rows
        rows.append(clean)
    
    if not hasattr(path, 'getvalue'):
        f.close()

    return rows

def write_csv(cards: List["Card"], path: Optional[str] = None) -> str:
    output = io.StringIO()
    w = csv.DictWriter(output, fieldnames=ALL_COLS)
    w.writeheader()
    for c in cards:
        w.writerow({k: getattr(c, k, "") or "" for k in ALL_COLS})
    
    content = output.getvalue()
    
    if path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8-sig", newline="") as f:
            f.write(content)

    return content
