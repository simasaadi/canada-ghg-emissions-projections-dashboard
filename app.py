import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="GHG Emissions Dashboard", layout="wide")
st.title("Canada GHG Emissions Dashboard")

# --- Load and combine sheets ---
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

# ---- Sidebar filters ----
# ---------- Pretty sector order & common helpers ----------
SECTOR_ORDER = [
    "Agriculture", "Buildings", "Electricity", "Heavy Industry",
    "Oil and Gas", "Transportation", "WCI Credits", "Waste and Others"
]
SECTOR_COLORS = {
    "Agriculture":        "#e6b800",   # yellow-gold
    "Buildings":          "#76b7b2",   # teal
    "Electricity":        "#1f77b4",   # blue
    "Heavy Industry":     "#f2cf62",   # light gold
    "Oil and Gas":        "#4e79a7",   # deeper blue (optional)
    "Transportation":     "#d62728",   # red
    "WCI Credits":        "#9467bd",   # purple
    "Waste and Others":   "#2ca02c",   # green
}


def tidy_sectors(df_in):
    df2 = df_in.copy()
    # normalize sector labels just in case
    df2["Economic Sector"] = df2["Economic Sector"].str.strip()
    # keep only known sectors (avoids totals/NA lines)
    df2 = df2[df2["Economic Sector"].isin(SECTOR_ORDER)]
    # categorical order for nicer legends/stack order
    df2["Economic Sector"] = pd.Categorical(df2["Economic Sector"], SECTOR_ORDER, ordered=True)
    return df2

# ---------- Sidebar filters ----------
scenarios = sorted(df["Scenario"].unique())
provinces = ["All provinces"] + sorted(df["Province"].unique())
sectors = ["All sectors"] + SECTOR_ORDER
years = sorted([int(y) for y in df["Year"].dropna().unique()])

scn = st.sidebar.selectbox("Scenario", scenarios, index=0)
prov = st.sidebar.selectbox("Province", provinces, index=0)
sect = st.sidebar.selectbox("Sector", sectors, index=0)
yr = st.sidebar.slider("Year for bar charts", min_value=min(years), max_value=max(years), value=2030, step=1)

# base filtered frame for the chosen scenario
df_base = df[df["Scenario"] == scn].copy()
if prov != "All provinces":
    df_base = df_base[df_base["Province"] == prov]
if sect != "All sectors":
    df_base = df_base[df_base["Economic Sector"] == sect]

df_base = tidy_sectors(df_base)

st.markdown("### Canada GHG Emissions Dashboard")

# ----------------- Tabs for the “pro” visuals -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Stacked Area (Additional Measures)",
    "Δ Heatmap (Add. − Ref.)",
    "Provinces (Bar)",
    "National Trend (Detailed vs Summary)*"
])

# -------- Tab 1: Stacked area like the PNG (Additional Measures) --------
# -------- Tab 1: Stacked area like the PNG (Additional Measures) --------
with tab1:
    st.caption("Sectoral Emissions — Additional Measures (mirrors the PNG style)")

    df_add = df[df["Scenario"].str.contains("Additional", case=False, regex=True)].copy()
    if prov != "All provinces":
        df_add = df_add[df_add["Province"] == prov]
    df_add = tidy_sectors(df_add)

    # Aggregate across provinces (national total) for comparability with the PNG
    area = df_add.groupby(["Year", "Economic Sector"], as_index=False)["Emissions"].sum()

    if area.empty:
        st.info("No data for this filter.")
    else:
        fig2 = px.area(
            area.sort_values(["Year", "Economic Sector"]),
            x="Year",
            y="Emissions",
            color="Economic Sector",
            category_orders={"Economic Sector": SECTOR_ORDER},
            # comment this line out if you didn't define SECTOR_COLORS
            color_discrete_map=SECTOR_COLORS,
            title="Sectoral Emissions — Additional Measures",
        )
        fig2.update_layout(legend_title_text="", margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig2, use_container_width=True)


# -------- Tab 2: Δ Heatmap (Additional Measures − Reference) --------
# -------- Tab 2: Δ Heatmap (Additional Measures − Reference) --------
with tab2:
    st.caption("Scenario Delta Heatmap — (Additional Measures − Reference) by Sector & Year")

    # DEBUG: show scenarios we have (remove after you confirm)
    st.write("Scenarios found:", sorted(df["Scenario"].unique()))

    dtmp = tidy_sectors(df.copy())

    # National totals to mirror the PNG
    wide_nat = dtmp.groupby(["Year", "Economic Sector", "Scenario"], as_index=False)["Emissions"].sum()
    wide_p = wide_nat.pivot_table(
        index=["Year", "Economic Sector"], columns="Scenario", values="Emissions"
    ).reset_index()

    # Robust scenario pickers
    def pick_col(cols, patterns):
        # choose the longest column name that matches ALL patterns
        cands = []
        for c in cols:
            name = str(c).lower()
            if all(p.lower() in name for p in patterns):
                cands.append(c)
        if not cands:
            return None
        return max(cands, key=lambda x: len(str(x)))

    # try several patterns to be safe
    ref_col = (pick_col(wide_p.columns, ["reference"]) or
               pick_col(wide_p.columns, ["ref"]))  # fallback
    add_col = (pick_col(wide_p.columns, ["additional"]) or
               pick_col(wide_p.columns, ["add"]))  # fallback

    if not ref_col or not add_col:
        st.error(
            "Could not find the scenario columns for Reference / Additional Measures. "
            "Make sure your scenario names include words like 'Reference' and 'Additional'."
        )
        st.write("Available columns:", list(wide_p.columns))
    else:
        wide_p["Delta"] = wide_p[add_col] - wide_p[ref_col]
        heat = (wide_p
                .pivot(index="Economic Sector", columns="Year", values="Delta")
                .reindex(SECTOR_ORDER))

        import plotly.graph_objects as go
        z = heat.values
        x = heat.columns.astype(int).tolist()
        y = heat.index.tolist()

        fig_hm = go.Figure(data=go.Heatmap(
            z=z, x=x, y=y, colorscale="RdYlGn_r", colorbar=dict(title="Δ (Mt CO₂e)")
        ))
        fig_hm.update_layout(
            title="Scenario Delta Heatmap — Additional − Reference (National Totals)",
            xaxis_title="Year", yaxis_title="Economic Sector",
            margin=dict(l=80, r=20, t=60, b=40)
        )
        st.plotly_chart(fig_hm, use_container_width=True)



# -------- Tab 3: Province bar (chosen year & scenario) --------
with tab3:
    st.caption(f"Emissions by Province — {scn} — {yr}")
    prov_bar = df[(df["Scenario"] == scn) & (df["Year"] == yr)].groupby("Province", as_index=False)["Emissions"].sum()
    prov_bar = prov_bar.sort_values("Emissions", ascending=False)
    fig4 = px.bar(prov_bar, x="Province", y="Emissions", title=f"Emissions by Province — {scn} — {yr}")
    fig4.update_layout(xaxis_tickangle=-35, margin=dict(l=20,r=20,t=60,b=80))
    st.plotly_chart(fig4, use_container_width=True)

# -------- Tab 4: National trend (Detailed vs Scenario Summary) --------
with tab4:
    st.caption("(*Requires the Tab3 national summary file to compare Detailed vs Scenario Summary*)")
    st.write("This chart matches the multi-line figure in the PNGs. To enable it, make sure the file **data/Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx** is present and contains fields for Year, Sector/Total, Scenario, and a marker of ‘Detailed’ vs ‘Scenario summary’. Then plot both on one figure. If your column names differ, tweak the code accordingly.")
    st.info("You already uploaded the Tab3 file — if you want, I can generate this plot too. For now the three visuals above mirror the PNGs.")

