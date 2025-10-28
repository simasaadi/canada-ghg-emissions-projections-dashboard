
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GHG Emissions Dashboard", layout="wide")
st.title("Canada GHG Emissions Dashboard")

# Load and combine sheets
path = "/mnt/data/Tab2_detailed_GHG_emissions_GES_detaillees_EN.xlsx"
sheets = pd.ExcelFile(path).sheet_names
frames = []
for s in sheets:
    df_s = pd.read_excel(path, sheet_name=s)
    df_s.columns = [str(c).strip() for c in df_s.columns]
    if "Year" not in df_s.columns or "Economic Sector" not in df_s.columns:
        continue
    scenario_cols = [c for c in df_s.columns if c not in ["Year", "Economic Sector"]]
    long = df_s.melt(id_vars=["Year", "Economic Sector"], value_vars=scenario_cols, var_name="Scenario", value_name="Emissions")
    long["Province"] = s
    frames.append(long)

df = pd.concat(frames, ignore_index=True)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
df["Emissions"] = pd.to_numeric(df["Emissions"], errors="coerce")
df["Economic Sector"] = df["Economic Sector"].astype(str).str.strip()
df["Scenario"] = df["Scenario"].astype(str).str.strip()
df["Province"] = df["Province"].astype(str).str.strip()

# Sidebar filters
scenarios = sorted(df["Scenario"].unique())
provinces = ["All provinces"] + sorted(df["Province"].unique())
sectors = ["All sectors"] + sorted(df["Economic Sector"].unique())
years = sorted([int(y) for y in df["Year"].dropna().unique()])

scn = st.sidebar.selectbox("Scenario", scenarios, index=0)
prov = st.sidebar.selectbox("Province", provinces, index=0)
sect = st.sidebar.selectbox("Sector", sectors, index=0)
yr = st.sidebar.slider("Year for bar charts", min_value=min(years), max_value=max(years), value=min(years), step=1)

df_f = df[df["Scenario"] == scn].copy()
if prov != "All provinces":
    df_f = df_f[df_f["Province"] == prov]
if sect != "All sectors":
    df_f = df_f[df_f["Economic Sector"] == sect]

# Top row
c1, c2 = st.columns(2)
with c1:
    total = df_f.groupby("Year", as_index=False)["Emissions"].sum()
    fig1 = px.line(total, x="Year", y="Emissions", markers=True, title=f"Total Emissions Trend — {scn} — {prov} — {sect}")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    area = df_f.groupby(["Year","Economic Sector"], as_index=False)["Emissions"].sum()
    if len(area):
        fig2 = px.area(area, x="Year", y="Emissions", color="Economic Sector", title=f"Emissions by Sector — {scn} — {prov}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No sector data available after filtering.")

# Bottom row
c3, c4 = st.columns(2)
with c3:
    # Sector bar for selected year
    sec_bar = df[df["Scenario"] == scn].copy()
    if prov != "All provinces":
        sec_bar = sec_bar[sec_bar["Province"] == prov]
    sec_bar = sec_bar[sec_bar["Year"] == yr].groupby("Economic Sector", as_index=False)["Emissions"].sum()
    fig3 = px.bar(sec_bar, x="Economic Sector", y="Emissions", title=f"Emissions by Sector — {scn} — {prov} — {yr}")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    # Province bar for selected year
    prov_bar = df[(df["Scenario"] == scn) & (df["Year"] == yr)].groupby("Province", as_index=False)["Emissions"].sum()
    fig4 = px.bar(prov_bar, x="Province", y="Emissions", title=f"Emissions by Province — {scn} — {yr}")
    st.plotly_chart(fig4, use_container_width=True)
