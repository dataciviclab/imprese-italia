"""Data access layer — Imprese Italia dashboard.

Multi-dataset via lab_connectors: GCS default, out/ locale come fallback.
I derivati (bilancio, composizione, RCA) vivono nel compose demografia_imprese.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.duckdb.queries import (
    detect_local_root,
    load_mart_table as _load_mart_table,
    query_clean as _query_clean,
)
from lab_connectors.formatters import fmt_num, fmt_pct
from lab_connectors.registry import load_registry

ROOT = Path(__file__).parent.parent
PREFIX = "imprese-italia/"
YEARS = (2026,)
LOCAL_ROOT = detect_local_root(repo_root=ROOT)

# Etichette ATECO 2 (sezioni standard + codici fonte)
ATECO_LABELS = {
    "A": "Agricoltura e pesca",
    "B": "Estrazione minerale",
    "C": "Industria manifatturiera",
    "D": "Energia elettrica e gas",
    "E": "Acqua e rifiuti",
    "F": "Costruzioni",
    "G": "Commercio e riparazione",
    "H": "Trasporto e magazzinaggio",
    "I": "Alberghi e ristorazione",
    "J": "Informazione e comunicazione",
    "K": "Intermediazione finanziaria",
    "L": "Attività immobiliari",
    "M": "Attività professionali",
    "N": "Servizi di supporto",
    "O": "Amministrazione pubblica",
    "P": "Istruzione",
    "Q": "Sanità e servizi sociali",
    "R": "Arte, sport e intrattenimento",
    "S": "Altri servizi",
    "T": "Famiglie come datori di lavoro",
    "U": "Organizzazioni extraterritoriali",
    "V": "Codice fonte raro",
    "X": "Non classificabili",
    "TOTAL": "Totale",
}

# Codici da escludere dai ranking principali (caveat UI)
SPECIAL_CODES = frozenset({"X", "V", "U", "P"})


def ateco_label(code: str) -> str:
    return ATECO_LABELS.get(code, code)


def load_registry_obj():
    return load_registry(ROOT / "registry" / "registry.json")


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Carica un mart table da GCS (o out/ locale se presente)."""
    return _load_mart_table(slug, table, year, prefix=PREFIX, local_root=LOCAL_ROOT)


@st.cache_data(ttl=3600, show_spinner=False)
def load_bilancio() -> pd.DataFrame:
    return load_mart("demografia_imprese", "mart_bilancio_mensile")


@st.cache_data(ttl=3600, show_spinner=False)
def load_composizione() -> pd.DataFrame:
    return load_mart("demografia_imprese", "mart_composizione_ateco")


@st.cache_data(ttl=3600, show_spinner=False)
def load_specializzazione() -> pd.DataFrame:
    return load_mart("demografia_imprese", "mart_specializzazione")


@st.cache_data(ttl=3600, show_spinner=False)
def load_codici_anomali() -> pd.DataFrame:
    return load_mart("demografia_imprese", "mart_codici_anomali")


@st.cache_data(ttl=3600, show_spinner=False)
def load_serie_stock_italia() -> pd.DataFrame:
    return load_mart("camcom_stock_italia", "mart_serie_italia_ateco")


@st.cache_data(ttl=3600, show_spinner=False)
def load_serie_territorio() -> pd.DataFrame:
    return load_mart("camcom_stock_italia", "mart_serie_territorio")


@st.cache_data(ttl=3600, show_spinner=False)
def load_serie_comune() -> pd.DataFrame:
    return load_mart("camcom_stock_marche", "mart_serie_comune")


@st.cache_data(ttl=3600, show_spinner=False)
def load_variazione() -> pd.DataFrame:
    return load_mart("camcom_variazione", "mart_serie_italia_ateco")


@st.cache_data(ttl=3600, show_spinner=False)
def query(slug: str, sql: str, years: tuple[int, ...] = YEARS) -> pd.DataFrame:
    """SQL sul clean layer di un dataset (cached 1h)."""
    return _query_clean(slug, sql, list(years), prefix=PREFIX, local_root=LOCAL_ROOT)


def latest_date(df: pd.DataFrame, col: str = "data"):
    if df is None or df.empty or col not in df.columns:
        return None
    return df[col].max()


def italia_stock_trend() -> pd.DataFrame:
    """Serie stock ITALIA (TOTAL) da mart_serie_territorio."""
    df = load_serie_territorio()
    if df.empty:
        return df
    out = df[df["territorio"] == "ITALIA"][["data", "imprese"]].copy()
    return out.sort_values("data")


def bilancio_italia_latest(n: int = 10) -> pd.DataFrame:
    """Ultimo mese bilancio Italia, esclusi codici speciali se presenti."""
    df = load_bilancio()
    if df.empty:
        return df
    d = df["data"].max()
    out = df[df["data"] == d].copy()
    out = out[~out["ateco"].isin(SPECIAL_CODES)]
    return out.sort_values("netto", ascending=False).head(n)


def composizione_italia_latest(top_n: int = 12) -> pd.DataFrame:
    df = load_composizione()
    if df.empty:
        return df
    d = df["data"].max()
    out = df[(df["data"] == d) & (df["territorio"] == "ITALIA")].copy()
    out = out[~out["ateco"].isin(SPECIAL_CODES)]
    return out.sort_values("imprese", ascending=False).head(top_n)


def specializzazione_top(bottom: bool = False, n: int = 10) -> pd.DataFrame:
    """Top settori per RCA (bottom=False) o i più sotto media (bottom=True)."""
    df = load_specializzazione()
    if df.empty:
        return df
    out = df[~df["ateco"].isin(SPECIAL_CODES)].copy()
    return out.sort_values("rca", ascending=bottom).head(n)


def province_latest(top_n: int = 15) -> pd.DataFrame:
    df = load_serie_territorio()
    if df.empty:
        return df
    d = df["data"].max()
    out = df[(df["data"] == d) & (df["territorio_tipo"] == "PROVINCIA")].copy()
    return out.sort_values("imprese", ascending=False).head(top_n)


def regioni_latest() -> pd.DataFrame:
    df = load_serie_territorio()
    if df.empty:
        return df
    d = df["data"].max()
    out = df[(df["data"] == d) & (df["territorio_tipo"] == "REGIONE")].copy()
    return out.sort_values("imprese", ascending=False)


def comune_label(territorio: str) -> str:
    """'AN-02 Ancona' → 'Ancona'; filtra le voci non classificate."""
    import re

    name = re.sub(r"^[A-Z]{2}-\d+\s+", "", str(territorio)).strip()
    if "non classificat" in name.lower():
        return ""
    return name


def comuni_marche_latest(top_n: int = 15) -> pd.DataFrame:
    df = load_serie_comune()
    if df.empty:
        return df
    d = df["data"].max()
    out = df[df["data"] == d].copy()
    out["comune"] = out["territorio"].map(comune_label)
    out = out[out["comune"] != ""]
    return out.sort_values("imprese", ascending=False).head(top_n)


def fmt_delta_pct(curr, prev) -> str | None:
    if curr is None or prev is None or prev == 0:
        return None
    return f"{(curr / prev - 1) * 100:+.1f}%"


# Re-export formatters standard Lab
__all__ = [
    "PREFIX",
    "YEARS",
    "SPECIAL_CODES",
    "ATECO_LABELS",
    "ateco_label",
    "load_registry_obj",
    "load_mart",
    "load_bilancio",
    "load_composizione",
    "load_specializzazione",
    "load_codici_anomali",
    "load_serie_stock_italia",
    "load_serie_territorio",
    "load_serie_comune",
    "load_variazione",
    "query",
    "latest_date",
    "italia_stock_trend",
    "bilancio_italia_latest",
    "composizione_italia_latest",
    "specializzazione_top",
    "province_latest",
    "regioni_latest",
    "comuni_marche_latest",
    "comune_label",
    "fmt_delta_pct",
    "fmt_num",
    "fmt_pct",
]
