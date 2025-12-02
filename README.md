Canada GHG Emissions Projections — Policy Scenarios, Sectors & Provinces (ECCC)

Interactive dashboard analyzing Canada’s greenhouse-gas emissions using open datasets from Environment and Climate Change Canada (ECCC).
Built with Python, Plotly, and Streamlit, this tool lets users explore national, sectoral, and provincial emissions trajectories under multiple policy scenarios.

Key Questions This Dashboard Answers

How do national emissions change under Reference vs Additional Measures scenarios?

Which sectors dominate future emissions, and how do their shares shift over time?

What is the emissions gap between scenarios (Additional Measures − Reference)?

Which provinces are projected to be the highest emitters in 2030 under the Reference scenario?

Live Interactive App

Open the app to explore scenarios, sectors, provinces, and year-by-year projections.

Static HTML Version

A single-file export of the full dashboard:
https://simasaadi.github.io/canada-ghg-emissions-projections-dashboard/advanced_ghg_dashboard.html

How to Run Locally
pip install -r requirements.txt
streamlit run app.py

Repository Structure

app.py — main Streamlit application with filters and interactive charts

advanced_ghg_dashboard.html — standalone HTML version of the dashboard

requirements.txt — Python dependencies

images/ — optional static figures (not required for running the app)

data/ — ECCC Excel files (add locally; not stored in the repo)

Data Sources

Sectoral and provincial projections (detailed):
Tab2_detailed_GHG_emissions_GES_detaillees_EN.xlsx

National scenario summaries:
Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx

These datasets come from the Government of Canada’s official emissions modelling suite.

Created and maintained by Sima Saadi
LinkedIn
