"""Query SQL — Interroga clean e mart del repo."""

from lab_connectors.duckdb.sql_page import render_sql_query
from sources import PREFIX, load_registry_obj

registry = load_registry_obj()

render_sql_query(
    registry=registry,
    prefix=PREFIX,
    default_slug="camcom_stock_italia",
    title="🧪 Query SQL",
    description=(
        "Interroga i dati di Imprese Italia. "
        "Sul clean layer usa ``clean_input``; i mart analitici del compose "
        "``demografia_imprese`` sono disponibili come tabelle mart "
        "(bilancio, composizione, specializzazione, codici anomali)."
    ),
)
