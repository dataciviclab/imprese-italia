"""Regressione: i CSV wide camcom vengono unpivotati correttamente in clean."""

from __future__ import annotations

import calendar
import csv
import re
from datetime import date
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "out" / "data" / "raw"
CLEAN_DIR = ROOT / "out" / "data" / "clean"

DATE_PATTERNS = {
    "dd/mm/yyyy": re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    "yyyy-mm": re.compile(r"^\d{4}-\d{2}$"),
}

DATASETS = {
    "camcom_stock_italia": ("imprese", "dd/mm/yyyy", True),
    "camcom_stock_marche": ("imprese", "dd/mm/yyyy", True),
    "camcom_iscrizioni": ("nuove_imprese", "yyyy-mm", True),
    "camcom_cancellazioni": ("cessazioni", "yyyy-mm", True),
    "camcom_variazione": ("variazione_pct", "dd/mm/yyyy", False),
}


def _latest_year_dir(root: Path, dataset: str) -> Path | None:
    dirs = sorted(p for p in (root / dataset).glob("*") if p.is_dir() and p.name.isdigit())
    return dirs[-1] if dirs else None


def _read_raw(dataset: str, fmt: str) -> tuple[int, list[str]] | None:
    year_dir = _latest_year_dir(RAW_DIR, dataset)
    if year_dir is None:
        return None
    raw_path = year_dir / "raw_input.csv"
    if not raw_path.exists():
        return None
    with raw_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter=";")
        header = next(reader, [])
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    pattern = DATE_PATTERNS[fmt]
    date_headers = [cell.strip() for cell in header[2:] if pattern.match(cell.strip())]
    return len(rows), date_headers


def _clean_path(dataset: str) -> Path | None:
    year_dir = _latest_year_dir(CLEAN_DIR, dataset)
    if year_dir is None:
        return None
    files = sorted(year_dir.glob("*_clean.parquet"))
    return files[-1] if files else None


def _parse_header_date(value: str, fmt: str) -> date:
    if fmt == "yyyy-mm":
        year, month = (int(part) for part in value.split("-"))
        return date(year, month, calendar.monthrange(year, month)[1])
    day, month, year = (int(part) for part in value.split("/"))
    return date(year, month, day)


@pytest.mark.parametrize(
    "dataset,value_col,fmt,complete",
    [(name, *spec) for name, spec in DATASETS.items()],
    ids=list(DATASETS),
)
def test_clean_unpivot(dataset: str, value_col: str, fmt: str, complete: bool) -> None:
    raw = _read_raw(dataset, fmt)
    clean = _clean_path(dataset)
    if raw is None or clean is None:
        pytest.skip(f"Output non generato: {dataset}")

    raw_rows, date_headers = raw
    assert date_headers, f"{dataset}: nessuna colonna data nel raw"
    expected_rows = raw_rows * len(date_headers)

    con = duckdb.connect()
    rows, months, min_data, max_data, nulls = con.execute(
        f"""
        SELECT count(*), count(DISTINCT data), min(data), max(data),
               count(*) FILTER (WHERE {value_col} IS NULL)
        FROM read_parquet('{clean}')
        """
    ).fetchone()

    if complete:
        assert rows == expected_rows, f"{dataset}: {rows} righe, attese {expected_rows}"
        assert months == len(date_headers)
        assert min_data == _parse_header_date(date_headers[0], fmt)
    else:
        assert 0 < rows <= expected_rows, f"{dataset}: {rows} righe, max {expected_rows}"
        assert 0 < months <= len(date_headers)
    assert max_data == _parse_header_date(date_headers[-1], fmt)
    assert nulls == 0, f"{dataset}: {nulls} valori NULL in {value_col}"
