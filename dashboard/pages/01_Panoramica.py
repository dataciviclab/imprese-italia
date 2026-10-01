"""Panoramica — Control room della demografia d'impresa italiana."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sources import (
    ateco_label,
    bilancio_italia_latest,
    composizione_italia_latest,
    fmt_delta_pct,
    fmt_num,
    italia_stock_trend,
    load_bilancio,
    load_serie_stock_italia,
)

st.title("🇮🇹 Imprese Italia")
st.caption(
    "Quante imprese nascono, crescono e muoiono in Italia. "
    "Serie mensili da Registro delle Imprese (InfoCamere / CCIAA Marche).",
)

# ── KPI ─────────────────────────────────────────────────────────────────────
trend = italia_stock_trend()
bil = load_bilancio()

if trend.empty:
    st.warning("Nessuno stock disponibile.")
    st.stop()

latest = trend.iloc[-1]
prev_y = trend[trend["data"] == latest["data"] - pd.DateOffset(months=12)]
stock_prev = float(prev_y["imprese"].iloc[0]) if not prev_y.empty else None
delta = fmt_delta_pct(float(latest["imprese"]), stock_prev)

# netto flussi ultimo mese Italia (tutti gli ATECO standard)
if not bil.empty:
    d_bil = bil["data"].max()
    netto = bil[(bil["data"] == d_bil) & (~bil["ateco"].isin({"X", "V", "U", "P", "TOTAL"}))]
    netto_tot = float(netto["netto"].sum()) if not netto.empty else None
    iscr = float(netto["iscrizioni"].sum()) if not netto.empty else None
    cess = float(netto["cessazioni"].sum()) if not netto.empty else None
else:
    netto_tot = iscr = cess = None

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Imprese attive", fmt_num(latest["imprese"]), delta=delta)
with k2:
    st.metric("Iscrizioni (mese)", fmt_num(iscr) if iscr is not None else "—")
with k3:
    st.metric("Cancellazioni (mese)", fmt_num(cess) if cess is not None else "—")
with k4:
    st.metric(
        "Netto flussi",
        fmt_num(netto_tot) if netto_tot is not None else "—",
        delta_color="normal" if (netto_tot or 0) >= 0 else "inverse",
    )

st.caption(
    f"Riferimento: {latest['data'].date()} · "
    "Caveat: le cancellazioni di dicembre/gennaio riflettono anche stocktaking di registro.",
)

# ── Trend stock Italia ──────────────────────────────────────────────────────
st.subheader("Serie storica — stock Italia")
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=trend["data"],
        y=trend["imprese"],
        mode="lines+markers",
        name="Imprese attive",
        line={"width": 3, "color": "#2563eb"},
        hovertemplate="%{x|%b %Y}<br>%{y:,.0f} imprese<extra></extra>",
    ),
)
fig.update_layout(
    height=380,
    margin={"t": 20, "b": 40},
    yaxis_title="Imprese",
    xaxis_title="",
    hovermode="x unified",
)
st.plotly_chart(fig, width="stretch")

# ── Composizione + bilancio affiancati ──────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Composizione settoriale (latest)")
    comp = composizione_italia_latest(top_n=10)
    if comp.empty:
        st.info("Nessun dato composizione.")
    else:
        comp = comp.copy()
        comp["settore"] = comp["ateco"].map(ateco_label)
        fig = go.Figure(
            go.Bar(
                x=comp["imprese"],
                y=comp["settore"],
                orientation="h",
                marker_color="#2563eb",
                text=[fmt_num(v) for v in comp["imprese"]],
                textposition="outside",
                hovertemplate="%{y}<br>%{x:,.0f} imprese<extra></extra>",
            ),
        )
        fig.update_layout(
            height=420,
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            xaxis_title="Imprese",
            yaxis={"autorange": "reversed"},
        )
        st.plotly_chart(fig, width="stretch")

with col_r:
    st.subheader("Bilancio per settore (latest)")
    bal = bilancio_italia_latest(n=10)
    if bal.empty:
        st.info("Nessun dato bilancio.")
    else:
        bal = bal.copy()
        bal["settore"] = bal["ateco"].map(ateco_label)
        colors = ["#059669" if v >= 0 else "#d97706" for v in bal["netto"]]
        fig = go.Figure(
            go.Bar(
                x=bal["netto"],
                y=bal["settore"],
                orientation="h",
                marker_color=colors,
                text=[fmt_num(v) for v in bal["netto"]],
                textposition="outside",
                hovertemplate="%{y}<br>netto %{x:,.0f}<extra></extra>",
            ),
        )
        fig.update_layout(
            height=420,
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            xaxis_title="Iscrizioni − Cancellazioni",
            yaxis={"autorange": "reversed"},
        )
        st.plotly_chart(fig, width="stretch")

# ── Variazioni top/bottom ───────────────────────────────────────────────────
st.subheader("Variazione YoY per settore (latest)")
ser = load_serie_stock_italia()
if ser.empty:
    st.info("Nessuna serie stock.")
else:
    d = ser["data"].max()
    curr = ser[ser["data"] == d].set_index("ateco")["imprese"]
    prev = ser[ser["data"] == d - pd.DateOffset(months=12)].set_index("ateco")["imprese"]
    rows = []
    for code in curr.index:
        if code in {"TOTAL", "X", "V", "U", "P"}:
            continue
        c, p = float(curr[code]), float(prev.get(code, float("nan")))
        if pd.isna(p) or p == 0:
            continue
        rows.append(
            {
                "ateco": code,
                "settore": ateco_label(code),
                "yoy_pct": (c / p - 1) * 100,
                "imprese": c,
            },
        )
    if rows:
        yoy = pd.DataFrame(rows).sort_values("yoy_pct")
        top = yoy.tail(8)
        bottom = yoy.head(8)
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(
                go.Bar(
                    x=top["yoy_pct"],
                    y=top["settore"],
                    orientation="h",
                    marker_color="#059669",
                    text=[f"{v:+.1f}%" for v in top["yoy_pct"]],
                    textposition="outside",
                ),
            )
            fig.update_layout(title="In crescita", height=360, margin={"t": 40, "b": 20})
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig = go.Figure(
                go.Bar(
                    x=bottom["yoy_pct"],
                    y=bottom["settore"],
                    orientation="h",
                    marker_color="#d97706",
                    text=[f"{v:+.1f}%" for v in bottom["yoy_pct"]],
                    textposition="outside",
                ),
            )
            fig.update_layout(title="In contrazione", height=360, margin={"t": 40, "b": 20})
            st.plotly_chart(fig, width="stretch")

st.caption(
    "Codici rari X/V/U/P esclusi dai ranking. "
    "Dettaglio in `mart_codici_anomali` (compose demografia_imprese).",
)
