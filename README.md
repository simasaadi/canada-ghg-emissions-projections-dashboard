# Canada GHG Emissions Projections — Policy Scenarios, Sectors & Provinces (ECCC)

Interactive dashboard built with **Python, Plotly, and Streamlit** using open datasets from **Environment and Climate Change Canada (ECCC)**.

## 🔎 Key Questions Answered
- How do national emissions evolve under the Reference vs Additional Measures scenarios?
- Which sectors contribute most to future emissions, and how does this change over time?
- What is the expected emissions difference (Additional Measures − Reference) by sector across years?
- Which provinces are projected to emit the most in 2030 under the Reference scenario?

## 🖼️ Visual Previews
![National Trend](images/01_national_trend_detailed_vs_summary.png)
![Sectoral Stacked Area — Additional Measures](images/02_sectoral_stacked_area.png)
![Scenario Delta Heatmap](images/03_heatmap_delta.png)
![Provincial Comparison](images/04_province_bar.png)

## 🚀 Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📂 Repository Contents
- `advanced_ghg_dashboard.html` — interactive single-file dashboard
- `app.py` — Streamlit app with filters for scenario, sector, province, and year
- `requirements.txt` — Python dependencies
- `images/` — static PNGs of the main figures
- `data/` — Excel files (ECCC projections) — add locally if needed

## 📊 Data Sources
- Detailed projections by sector & province: `Tab2_detailed_GHG_emissions_GES_detaillees_EN.xlsx`
- National scenario summary: `Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx`

## 🚀 Live Streamlit App

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20App-red?logo=streamlit)](https://canada-ghg-emissions-projections-dashboard-dhbdrslzfjzb8dnusog.streamlit.app)

Click the button above to open the fully interactive emissions dashboard.


### 🌐 GitHub Pages (HTML preview)
[View the static HTML dashboard](https://simasaadi.github.io/canada-ghg-emissions-projections-dashboard/advanced_ghg_dashboard.html)

Created and maintained by [Sima Saadi](https://www.linkedin.com/in/sima-saadi/) 

