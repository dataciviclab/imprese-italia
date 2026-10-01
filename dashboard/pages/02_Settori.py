"""Settori — Composizione, bilancio e specializzazione per ATECO 2."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sources import (
    SPECIAL_CODES,
    ateco_label,
    fmt_num,
    load_bilancio,
    load_composizione,
    load_specializzazione,
)

st.title("🏭 Settori")
st.markdown(
    "Composizione stock, bilancio demografico e specializzazione territoriale per sezione ATECO 2."
)

comp_all = load_composizione()
bil = load_bilancio()
spec = load_specializzazione()

if comp_all.empty:
    st.warning("Nessun dato settoriale disponibile.")
    st.stop()

dates = sorted(comp_all["data"].unique())
data_sel = st.selectbox("Mese", dates, index=len(dates) - 1)
hide_special = st.checkbox("Escludi codici rari (X/V/U/P)", value=True)

# ── Composizione ────────────────────────────────────────────────────────────
st.subheader(f"Stock Italia per settore — {pd.Timestamp(data_sel).date()}")
comp = comp_all[(comp_all["data"] == data_sel) & (comp_all["territorio"] == "ITALIA")].copy()
if hide_special:
    comp = comp[~comp["ateco"].isin(SPECIAL_CODES)]
comp = comp.sort_values("imprese", ascending=False)
comp["settore"] = comp["ateco"].map(ateco_label)

fig = px.bar(
    comp,
    x="settore",
    y="imprese",
    color="share_pct",
    color_continuous_scale="Blues",
    text="share_pct",
    text_auto=".1f",
    labels={"imprese": "Imprese", "share_pct": "Share %", "settore": ""},
)
fig.update_layout(height=420, margin={"t": 10, "b": 80}, xaxis_tickangle=-35)
st.plotly_chart(fig, width="stretch")

col_t, col_b = st.columns(2)

with col_t:
    st.dataframe(
        comp[["settore", "imprese", "share_pct"]].rename(
            columns={"settore": "Settore", "imprese": "Imprese", "share_pct": "Share %"}
        ),
        width="stretch",
        hide_index=True,
        height=360,
    )

with col_b:
    st.subheader("Bilancio iscrizioni − cessazioni")
    bal = bil[bil["data"] == data_sel].copy()
    if hide_special:
        bal = bal[~bal["ateco"].isin(SPECIAL_CODES)]
    bal = bal.sort_values("netto")
    bal["settore"] = bal["ateco"].map(ateco_label)
    bal["netto_fmt"] = bal["netto"].map(fmt_num)
    fig = go.Figure(
        go.Bar(
            x=bal["netto"],
            y=bal["settore"],
            orientation="h",
            marker_color=["#059669" if v >= 0 else "#d97706" for v in bal["netto"]],
            text=bal["netto_fmt"],
            textposition="outside",
        )
    )
    fig.update_layout(height=400, margin={"t": 10, "b": 20}, xaxis_title="Netto")
    st.plotly_chart(fig, width="stretch")

# ── Specializzazione Marche vs Italia ──────────────────────────────────────
st.divider()
st.subheader("Specializzazione Marche vs Italia (RCA)")
st.caption("RCA = share Marche / share Italia. >1 = sovrarappresentato nelle Marche.")

if spec.empty:
    st.info("Nessun dato specializzazione.")
else:
    s = spec.copy()
    if hide_special:
        s = s[~s["ateco"].isin(SPECIAL_CODES)]
    s = s.sort_values("rca", ascending=True)
    s["settore"] = s["ateco"].map(ateco_label)
    colors = ["#059669" if v >= 1 else "#d97706" for v in s["rca"]]
    fig = go.Figure(
        go.Bar(
            x=s["rca"],
            y=s["settore"],
            orientation="h",
            marker_color=colors,
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
                "stock_marche": "Stock Marche",
                "stock_italia": "Stock Italia",
                "share_marche_pct": "Share Marche %",
                "share_italia_pct": "Share Italia %",
                "rca": "RCA",
            }
        ),
        width="stretch",
        hide_index=True,
    )
