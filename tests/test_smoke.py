"""Smoke test contratti mart imprese-italia (incluso compose demografia)."""

from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
MART_DIR = ROOT / "out" / "data" / "mart"

MART_CONTRACTS = {
    "camcom_stock_italia": {
        "mart_provincia_ateco": {
            "min_rows": 50,
            "required_columns": ["territorio", "ateco", "data", "imprese"],
        },
        "mart_serie_italia_ateco": {
            "min_rows": 100,
            "required_columns": ["data", "ateco", "imprese", "totale", "share_pct"],
        },
        "mart_serie_territorio": {
            "min_rows": 100,
            "required_columns": ["data", "territorio", "territorio_tipo", "imprese"],
        },
    },
    "camcom_stock_marche": {
        "mart_comune_ateco": {
            "min_rows": 50,
            "required_columns": ["territorio", "ateco", "data", "imprese"],
        },
        "mart_serie_comune": {
            "min_rows": 100,
            "required_columns": ["data", "territorio", "imprese"],
        },
    },
    "camcom_iscrizioni": {
        "mart_iscrizioni_provincia": {
            "min_rows": 50,
            "required_columns": ["territorio", "ateco", "data", "nuove_imprese"],
        },
        "mart_serie_italia_ateco": {
            "min_rows": 100,
            "required_columns": ["data", "ateco", "nuove_imprese"],
        },
    },
    "camcom_cancellazioni": {
        "mart_cancellazioni_provincia": {
            "min_rows": 50,
            "required_columns": ["territorio", "ateco", "data", "cessazioni"],
        },
        "mart_serie_italia_ateco": {
            "min_rows": 100,
            "required_columns": ["data", "ateco", "cessazioni"],
        },
    },
    "camcom_variazione": {
        "mart_variazione_provincia": {
            "min_rows": 50,
            "required_columns": ["territorio", "ateco", "data", "variazione_pct"],
        },
        "mart_serie_italia_ateco": {
            "min_rows": 100,
            "required_columns": ["data", "ateco", "variazione_pct"],
        },
    },
    "demografia_imprese": {
        "mart_bilancio_mensile": {
            "min_rows": 100,
            "required_columns": [
                "data",
                "ateco",
                "stock",
                "iscrizioni",
                "cessazioni",
                "netto",
                "netto_pct_stock",
            ],
        },
        "mart_composizione_ateco": {
            "min_rows": 100,
            "required_columns": [
                "data",
                "territorio",
                "territorio_tipo",
                "ateco",
                "imprese",
                "totale",
                "share_pct",
            ],
        },
        "mart_specializzazione": {
            "min_rows": 10,
            "required_columns": [
                "data",
                "ateco",
                "stock_marche",
                "stock_italia",
                "share_marche_pct",
                "share_italia_pct",
                "rca",
            ],
        },
        "mart_codici_anomali": {
            "min_rows": 10,
            "required_columns": ["data", "ateco", "stock", "variazione_pct", "classe_ateco"],
        },
    },
}


def _find_mart_files(dataset: str, mart_name: str) -> list[Path]:
    pattern = MART_DIR / dataset
    if not pattern.exists():
        return []
    files: list[Path] = []
    for year_dir in pattern.iterdir():
        if year_dir.is_dir():
            files.extend(year_dir.glob(f"{mart_name}*.parquet"))
    return files


@pytest.mark.smoke
class TestMartContracts:
    @pytest.mark.parametrize(
        "dataset,mart_name,contract",
        [
            (ds, mart, contract)
            for ds, marts in MART_CONTRACTS.items()
            for mart, contract in marts.items()
        ],
        ids=[
            f"{ds}:{mart}"
            for ds, marts in MART_CONTRACTS.items()
            for mart in marts
        ],
    )
    def test_mart_contract(self, dataset: str, mart_name: str, contract: dict):
        files = _find_mart_files(dataset, mart_name)
        if not files:
            pytest.skip(f"Mart non generato: {dataset}/{mart_name}")

        con = duckdb.connect()
        paths = ", ".join(f"'{p}'" for p in files)
        df = con.sql(f"SELECT * FROM read_parquet([{paths}])").df()

        assert len(df) >= contract["min_rows"], (
            f"{dataset}/{mart_name}: {len(df)} righe < {contract['min_rows']}"
        )
        missing = [c for c in contract["required_columns"] if c not in df.columns]
        assert not missing, f"{dataset}/{mart_name}: colonne mancanti {missing}"


@pytest.mark.smoke
class TestComposeIntegrity:
    def test_bilancio_netto_consistente(self):
        files = _find_mart_files("demografia_imprese", "mart_bilancio_mensile")
        if not files:
            pytest.skip("mart_bilancio_mensile non generato")
        con = duckdb.connect()
        paths = ", ".join(f"'{p}'" for p in files)
        df = con.sql(
            f"""
            SELECT data, ateco, stock, iscrizioni, cessazioni, netto
            FROM read_parquet([{paths}])
            WHERE ateco = 'G'
            ORDER BY data DESC
            LIMIT 1
            """
        ).df()
        assert not df.empty
        row = df.iloc[0]
        assert row["netto"] == row["iscrizioni"] - row["cessazioni"]

    def test_specializzazione_rca_positive(self):
        files = _find_mart_files("demografia_imprese", "mart_specializzazione")
        if not files:
            pytest.skip("mart_specializzazione non generato")
        con = duckdb.connect()
        paths = ", ".join(f"'{p}'" for p in files)
        df = con.sql(
            f"SELECT ateco, rca FROM read_parquet([{paths}]) WHERE ateco NOT IN ('V','U')"
        ).df()
        assert not df.empty
        assert df["rca"].notna().any()
