Canada GHG Emissions Projections — Policy Scenarios, Sectors & Provinces (ECCC)

Interactive dashboard analyzing Canada's greenhouse-gas emissions using open datasets from Environment and Climate Change Canada (ECCC).
Built with Python, Plotly, and Streamlit.

Live Dashboard

Static HTML Version

A single-file export of the dashboard:
https://simasaadi.github.io/canada-ghg-emissions-projections-dashboard/advanced_ghg_dashboard.html

Key Questions This Dashboard Answers

How do national emissions evolve under Reference vs Additional Measures?

Which sectors contribute the most to future emissions?

How large is the emissions gap between scenarios (Additional Measures – Reference)?

Which provinces are projected to emit the most in 2030?

How to Run Locally
pip install -r requirements.txt
streamlit run app.py

Repository Structure
canada-ghg-emissions-projections-dashboard
│
├── app.py                       # Main Streamlit application
├── advanced_ghg_dashboard.html  # Standalone HTML dashboard
├── requirements.txt             # Python dependencies
│
├── images/                      # (Optional) static preview figures
└── data/                        # ECCC Excel files (add locally)

Data Sources

Sectoral & provincial projections
Tab2_detailed_GHG_emissions_GES_detaillees_EN.xlsx

National scenario summaries
Tab3_a1_megatonnes_ref_GHG_Scenarios_GES_EN.xlsx

Datasets sourced from the Government of Canada’s emissions modelling program.

Created and maintained by Sima Saadi
LinkedIn
