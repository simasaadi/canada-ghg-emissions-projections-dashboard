import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="GHG Emissions Dashboard", layout="wide")
st.title("Canada GHG Emissions Dashboard")

# --- Load and combine sheets from Tab2 (detailed by province & sector) ---
path = Path("data/Tab2_detailed_GHG_emissions_GES_detaillees_EN.xlsx")
if not path.exists():
    st.error("Data file not found. Please upload it to the 'data/' folder in your GitHub repo.")
    st.stop()

sheets = pd.ExcelFile(path).sheet_names
frames = []
for s in sheets:
    df_s = pd.read_excel(path, sheet_name=s)
    df_s.columns = [str(c).strip() for c in df_s.columns]
    if "Year" not in df_s.columns or "Economic Sector" not in df_s.columns:
        continue

    scenario_cols = [c for c in df_s.columns if c not in ["Year", "Economic Sector"]]
    long = df_s.melt(
        id_vars=["Year", "Economic Sector"],
        value_vars=scenario_cols,
        var_name="Scenario",
        value_name="Emissions",
    )
    long["Province"] = s
    frames.append(long)

df = pd.concat(frames, ignore_index=True)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
df["Emissions"] = pd.to_numeric(df["Emissions"], errors="coerce")
df["Economic Sector"] = df["Economic Sector"].astype(str).str.strip()
df["Scenario"] = df["Scenario"].astype(str).str.strip()
df["Province"] = df["Province"].astype(str).str.strip()

# --- Helpers / display options ---
SECTOR_ORDER = [
    "Agriculture", "Buildings", "Electricity", "Heavy Industry",
    "Oil and Gas", "Transportation", "WCI Credits", "Waste and Others"
]
SECTOR_COLORS = {
    "Agriculture":        "#e6b800",
    "Buildings":          "#76b7b2",
    "Electricity":        "#1f77b4",
    "Heavy Industry":     "#f2cf62",
    "Oil and Gas":        "#4e79a7",
    "Transportation":     "#d62728",
    "WCI Credits":        "#9467bd",
    "Waste and Others":   "#2ca02c",
}

def tidy_sectors(df_in: pd.DataFrame) -> pd.DataFrame:
    df2 = df_in.copy()
    df2["Economic Sector"] = df2["Economic Sector"].str.strip()
    df2 = df2[df2["Economic Sector"].isin(SECTOR_ORDER)]
    df2["Economic Sector"] = pd.Categorical(df2["Economic Sector"], SECTOR_ORDER, ordered=True)
    return df2

# --- Sidebar filters ---
scenarios = sorted(df["Scenario"].unique())
provinces = ["All provinces"] + sorted(df["Province"].unique())
sectors = ["All sectors"] + SECTOR_ORDER
years = sorted([int(y) for y in df["Year"].dropna().unique()])

scn = st.sidebar.selectbox("Scenario", scenarios, index=0)
prov = st.sidebar.selectbox("Province", provinces, index=0)
sect = st.sidebar.selectbox("Sector", sectors, index=0)
yr = st.sidebar.slider("Year for bar charts", min_value=min(years), max_value=max(years), value=2030, step=1)

# Base filtered frame for chosen scenario
df_base = df[df["Scenario"] == scn].copy()
if prov != "All provinces":
    df_base = df_base[df_base["Province"] == prov]
if sect != "All sectors":
    df_base = df_base[df_base["Economic Sector"] == sect]
df_base = tidy_sectors(df_base)

st.markdown("### Canada GHG Emissions Dashboard")

# --- Stacked area (Additional Measures) ---
st.markdown("### Sectoral Emissions - Additional Measures (mirrors the PNG style)")
df_add = df[df["Scenario"].str.contains("Additional", case=False, regex=True)].copy()
if prov != "All provinces":
    df_add = df_add[df_add["Province"] == prov]
df_add = tidy_sectors(df_add)
area = df_add.groupby(["Year", "Economic Sector"], as_index=False)["Emissions"].sum()

if area.empty:
    st.info("No data for this filter.")
else:
    fig2 = px.area(
        area.sort_values(["Year", "Economic Sector"]),
        x="Year", y="Emissions", color="Economic Sector",
        category_orders={"Economic Sector": SECTOR_ORDER},
        color_discrete_map=SECTOR_COLORS,
        title="Sectoral Emissions - Additional Measures",
    )
    fig2.update_layout(legend_title_text="", margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# --- Delta heatmap (Additional - Reference) ---
st.markdown("### Scenario Delta Heatmap - Additional minus Reference (by sector and year)")
dtmp = tidy_sectors(df.copy())
wide_nat = dtmp.groupby(["Year", "Economic Sector", "Scenario"], as_index=False)["Emissions"].sum()
wide_p = wide_nat.pivot_table(index=["Year", "Economic Sector"], columns="Scenario", values="Emissions").reset_index()

def pick(colset, must_have):
    cand = [c for c in colset if all(w.lower() in str(c).lower() for w in must_have)]
    return max(cand, key=lambda x: len(str(x))) if cand else None

ref_col = pick(wide_p.columns, ["reference"])
add_col = pick(wide_p.columns, ["additional"])

if not ref_col or not add_col:
    st.warning("Could not find clearly labeled Reference / Additional scenario columns.")
else:
    wide_p["Delta"] = wide_p[add_col] - wide_p[ref_col]
    heat = (
        wide_p.pivot(index="Economic Sector", columns="Year", values="Delta")
        .reindex(SECTOR_ORDER)
    )
    fig_hm = go.Figure(data=go.Heatmap(
        z=heat.values,
        x=heat.columns.astype(int).tolist(),
        y=heat.index.tolist(),
        colorscale="RdYlGn_r",
        colorbar=dict(title="Delta (Mt CO2e)")
    ))
    fig_hm.update_layout(
        title="Scenario Delta Heatmap - Additional minus Reference (National totals)",
        xaxis_title="Year",
        yaxis_title="Economic Sector",
        margin=dict(l=80, r=20, t=60, b=40)
    )
    st.plotly_chart(fig_hm, use_container_width=True)

# --- Provincial bar chart ---
st.markdown(f"### Emissions by Province - {scn} - {yr}")
prov_bar = (
    df[(df["Scenario"] == scn) & (df["Year"] == yr)]
    .groupby("Province", as_index=False)["Emissions"].sum()
    .sort_values("Emissions", ascending=False)
)
fig4 = px.bar(prov_bar, x="Province", y="Emissions", title=f"Emissions by Province - {scn} - {yr}")
fig4.update_layout(xaxis_tickangle=-35, margin=dict(l=20, r=20, t=60, b=80))
st.plotly_chart(fig4, use_container_width=True)

# --- National trend (Detailed vs Scenario Summary) from Tab3 ---
st.markdown("### National Trend (Detailed vs Scenario Summary)")
tab3_path = Path("data/Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx")
if not tab3_path.exists():
    st.warning("Tab3 file not found at data/Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx")
else:
    try:
        xls = pd.ExcelFile(tab3_path)
        t3 = pd.concat([pd.read_excel(tab3_path, sheet_name=sh) for sh in xls.sheet_names], ignore_index=True)

        t3.columns = [str(c).strip() for c in t3.columns]
        low2orig = {c.lower(): c for c in t3.columns}

        def pick_col(keywords):
            for lower_name, orig in low2orig.items():
                if all(k in lower_name for k in keywords):
                    return orig
            return None

        year_col   = pick_col(["year"])
        value_col  = pick_col(["emission"]) or pick_col(["megaton"]) or pick_col(["mt"])
        scen_col   = pick_col(["scenario"]) or pick_col(["case"])
        sector_col = pick_col(["sector"]) or pick_col(["category"]) or pick_col(["total"])
        detail_col = pick_col(["detailed"]) or pick_col(["summary"]) or pick_col(["detail"]) or pick_col(["source"])

        if year_col is None or value_col is None:
            st.warning("Could not detect Year or Emissions column in Tab3.")
        else:
            g = t3.copy()
            for c in [scen_col, sector_col, detail_col]:
                if c and c in g.columns:
                    g[c] = g[c].astype(str).str.strip()

            g[year_col] = pd.to_numeric(g[year_col], errors="coerce")
            g[value_col] = pd.to_numeric(g[value_col], errors="coerce")

            if detail_col is None:
                def infer_detail(s):
                    s = str(s).lower()
                    if "detailed" in s:
                        return "Detailed"
                    if "summary" in s:
                        return "Scenario summary"
                    return "Unknown"
                g["DetailType"] = g[scen_col].apply(infer_detail) if scen_col else "Unknown"
                detail_col = "DetailType"

            if scen_col is None:
                g["ScenarioName"] = "Scenario"
                scen_col = "ScenarioName"

            if sector_col and sector_col in g.columns:
                mask_total = g[sector_col].str.lower().isin(["total", "totals", "all sectors", "all"])
                if mask_total.any():
                    g = g[mask_total]

            def clean_scn(s):
                s = str(s)
                if ("Additional" in s) and ("Reference" not in s):
                    return "Additional Measures Case"
                if "Reference" in s:
                    return "Reference Case"
                return s

            g["Scenario_clean"] = g[scen_col].apply(clean_scn)
            g = g.dropna(subset=[year_col, value_col])

            gg = g.groupby([year_col, "Scenario_clean", detail_col], as_index=False)[value_col].sum()

            fig_nat = px.line(
                gg.sort_values([year_col, "Scenario_clean", detail_col]),
                x=year_col, y=value_col,
                color="Scenario_clean",
                line_dash=detail_col,
                title="National GHG Emissions - Detailed vs Scenario Summary"
            )
            fig_nat.update_layout(
                xaxis_title="Year",
                yaxis_title="Emissions (Mt CO2e)",
                legend_title_text="Scenario / Detail",
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig_nat, use_container_width=True)

    except Exception as e:
        st.error(f"Could not render the national trend from Tab3: {e}")
