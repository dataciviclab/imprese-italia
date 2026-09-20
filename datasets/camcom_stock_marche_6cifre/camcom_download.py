"""Download Stock Imprese Attive Marche 6 Cifre ATECO da opendata.marche.camcom.it.

CSV già in long format — nessun unpivot necessario.
NOTA: l'URL cambia ogni trimestre (es. 2026-06-30-Stock-...).
Aggiornare URL_DATA quando disponibile il nuovo snapshot.
"""
import sys
import urllib.request
from pathlib import Path

URL_DATA = "2026-06-30"
URL = f"https://opendata.marche.camcom.it/data/{URL_DATA}-Stock-Imprese-Attive-Marche.csv"


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print(f"Download: {URL}")
    req = urllib.request.Request(URL)
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")

    out = output or Path(__file__).parent.parent.parent.parent / "out" / "data" / "raw" / "camcom_stock_marche_6cifre" / "2026" / "raw_input.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(raw)

    lines = raw.count("\n")
    print(f"Scritto: {out} ({lines} righe, {out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
