"""Marche — Comuni, trend e confronto con l'Italia."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sources import (
    ateco_label,
    comune_label,
    comuni_marche_latest,
    fmt_num,
    load_serie_comune,
    load_serie_stock_italia,
    load_specializzazione,
)

st.title("📍 Marche")
st.markdown(
    "Demografia d'impresa nei 227 comuni delle Marche: ranking, trend e "
    "specializzazione settoriale vs media nazionale."
)

comuni_df = load_serie_comune()
spec = load_specializzazione()
stock_it = load_serie_stock_italia()

if comuni_df.empty:
    st.warning("Nessun dato comuni Marche.")
    st.stop()

dates = sorted(comuni_df["data"].unique())
data_sel = st.selectbox("Mese", dates, index=len(dates) - 1, key="mar_data")

# ── Top comuni ──────────────────────────────────────────────────────────────
st.subheader(f"Top comuni — {pd.Timestamp(data_sel).date()}")
top = comuni_marche_latest(top_n=15)

fig = go.Figure(
    go.Bar(
        x=top["imprese"],
        y=top["comune"],
        orientation="h",
        marker_color="#2563eb",
        text=[fmt_num(v) for v in top["imprese"]],
        textposition="outside",
    )
)
fig.update_layout(
    height=420,
    margin={"t": 10, "b": 20},
    xaxis_title="Imprese attive",
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig, width="stretch")

st.dataframe(
    top[["comune", "territorio", "imprese"]].rename(
        columns={"comune": "Comune", "territorio": "Codice", "imprese": "Imprese"}
    ),
    width="stretch",
    hide_index=True,
)

# ── Trend comune ────────────────────────────────────────────────────────────
st.divider()
st.subheader("Trend comune")
serie = comuni_df.copy()
serie["comune"] = serie["territorio"].map(comune_label)
serie = serie[serie["comune"] != ""]
all_comuni = sorted(serie["comune"].drop_duplicates())
# Default: comune più grande all'ultimo mese (evita "non classificato" a 0)
_latest = serie[serie["data"] == data_sel]
_default = (
    _latest.sort_values("imprese", ascending=False)["comune"].iloc[0]
    if not _latest.empty
    else (all_comuni[0] if all_comuni else None)
)
_index = all_comuni.index(_default) if _default in all_comuni else 0
comune_sel = st.selectbox("Comune", all_comuni, index=_index, key="mar_comune_trend")

serie_c = serie[serie["comune"] == comune_sel].sort_values("data")

if serie_c.empty:
    st.info("Nessuna serie per il comune selezionato.")
else:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=serie_c["data"],
            y=serie_c["imprese"],
            mode="lines+markers",
            name="Imprese",
            line=dict(width=3, color="#2563eb"),
        )
    )
    fig.update_layout(
        title=f"{comune_sel} — serie stock (ATECO TOTAL)",
        height=360,
        margin={"t": 40, "b": 30},
        yaxis_title="Imprese",
    )
    st.plotly_chart(fig, width="stretch")

# ── Specializzazione settori Marche ─────────────────────────────────────────
st.divider()
st.subheader("Settori nelle Marche (RCA)")

if spec.empty:
    st.info("Nessun dato specializzazione.")
else:
    s = spec[~spec["ateco"].isin({"X", "V", "U", "P"})].copy()
    s = s.sort_values("rca", ascending=False)
    s["settore"] = s["ateco"].map(ateco_label)
    st.dataframe(
        s[
            [
                "settore",
                "stock_marche",
                "stock_italia",
                "share_marche_pct",
                "share_italia_pct",
                "rca",
            ]
        ].rename(
            columns={
                "settore": "Settore",
                "stock_marche": "Marche",
                "stock_italia": "Italia",
                "share_marche_pct": "Share Mar %",
                "share_italia_pct": "Share Ita %",
                "rca": "RCA",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    fig = go.Figure(
        go.Bar(
            x=s["rca"],
            y=s["settore"],
            orientation="h",
            marker_color=["#059669" if v >= 1 else "#d97706" for v in s["rca"]],
            text=[f"{v:.2f}" for v in s["rca"]],
            textposition="outside",
        )
    )
    fig.add_vline(x=1.0, line_dash="dash", line_color="#6b7280")
    fig.update_layout(
        height=max(360, len(s) * 28),
        margin={"t": 10, "b": 20},
        xaxis_title="RCA",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, width="stretch")
