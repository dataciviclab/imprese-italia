"""Download Stock Imprese Attive Marche da opendata.marche.camcom.it.

Scarica CSV wide (comune x ATECO x mesi) e converte in long format.
"""
import csv
import sys
import urllib.request
from pathlib import Path

URL = "https://opendata.marche.camcom.it/data/Stock-Imprese-Attive-Marche.csv"


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print(f"Download: {URL}")
    req = urllib.request.Request(URL)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")

    reader = csv.reader(raw.splitlines(), delimiter=";")
    header = next(reader)
    date_cols = header[2:]

    out = output or Path(__file__).parent.parent.parent.parent / "out" / "data" / "raw" / "camcom_stock_marche" / "2026" / "raw_input.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["territorio", "ateco", "data", "imprese"])
        count = 0
        for row in reader:
            territorio = row[0].strip()
            ateco = row[1].strip()
            for i, val in enumerate(date_cols):
                val = val.strip()
                if val and territorio and ateco:
                    writer.writerow([territorio, ateco, val, row[i + 2].strip()])
                    count += 1

    print(f"Scritto: {out} ({count} righe, {out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
