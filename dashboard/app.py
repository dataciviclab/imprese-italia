#!/usr/bin/env python3
"""
Imprese Italia · Dashboard Streamlit
Demografia d'impresa: stock, flussi, composizione e specializzazione territoriale.
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Imprese Italia · Dashboard",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="imprese-italia",
    repo_url="https://github.com/dataciviclab/imprese-italia",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Settori.py", title="Settori", icon="🏭"),
        st.Page("pages/03_Territorio.py", title="Territorio", icon="🗺️"),
        st.Page("pages/04_Marche.py", title="Marche", icon="📍"),
    ],
    "Strumenti": [
        st.Page("pages/05_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.caption(
    "Fonte: opendata.marche.camcom.it — CCIAA Marche su dati InfoCamere (CC BY 4.0)"
)
pg.run()
