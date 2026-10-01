"""Territorio — Ranking province e regioni."""

import pandas as pd
import plotly.express as px
import streamlit as st

from sources import fmt_num, load_serie_territorio, province_latest, regioni_latest

st.title("🗺️ Territorio")
st.markdown("Stock imprese per provincia e regione. La serie storica è in `mart_serie_territorio`.")

df = load_serie_territorio()
if df.empty:
    st.warning("Nessun dato territoriale.")
    st.stop()

dates = sorted(df["data"].unique())
data_sel = st.selectbox("Mese", dates, index=len(dates) - 1, key="terr_data")

prov = df[(df["data"] == data_sel) & (df["territorio_tipo"] == "PROVINCIA")].copy()
reg = df[(df["data"] == data_sel) & (df["territorio_tipo"] == "REGIONE")].copy()
italia = df[(df["data"] == data_sel) & (df["territorio_tipo"] == "ITALIA")]

k1, k2, k3 = st.columns(3)
k1.metric("Province", fmt_num(len(prov)))
k2.metric("Regioni", fmt_num(len(reg)))
if not italia.empty:
    k3.metric("Stock Italia", fmt_num(italia["imprese"].iloc[0]))

# ── Mappa regioni ───────────────────────────────────────────────────────────
st.subheader(f"Mappe regioni — {pd.Timestamp(data_sel).date()}")
GEOJSON_URL = (
    "https://raw.githubusercontent.com/openpolis/geojson-italy/"
    "master/geojson/limits_IT_regions.geojson"
)

# normalizza nomi regioni verso geojson (reg_name)
_reg = reg.copy()
_reg["reg_name"] = _reg["territorio"].str.title().str.replace("’", "'", regex=False)
# casi noti
_rename = {
    "Valle D'aosta": "Valle d'Aosta",
    "Friuli-Venezia Giulia": "Friuli-Venezia Giulia",
    "Trentino-Alto Adige": "Trentino-Alto Adige/Südtirol",
    "Emilia-Romagna": "Emilia-Romagna",
}
_reg["reg_name"] = _reg["reg_name"].replace(_rename)

fig = px.choropleth(
    _reg,
    geojson=GEOJSON_URL,
    locations="reg_name",
    featureidkey="properties.reg_name",
    color="imprese",
    color_continuous_scale="Blues",
    hover_name="territorio",
    hover_data={"imprese": ":,.0f", "territorio": True},
    labels={"imprese": "Imprese"},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=480,
    coloraxis_colorbar=dict(title="Imprese"),
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, width="stretch")

# ── Ranking ─────────────────────────────────────────────────────────────────
col_p, col_r = st.columns(2)

with col_p:
    st.subheader("Top province")
    top_p = prov.sort_values("imprese", ascending=False).head(15)
    st.dataframe(
        top_p[["territorio", "imprese"]].rename(
            columns={"territorio": "Provincia", "imprese": "Imprese"}
        ),
        width="stretch",
        hide_index=True,
        height=420,
    )

with col_r:
    st.subheader("Regioni")
    st.dataframe(
        reg.sort_values("imprese", ascending=False)[["territorio", "imprese"]].rename(
            columns={"territorio": "Regione", "imprese": "Imprese"}
        ),
        width="stretch",
        hide_index=True,
        height=420,
    )
