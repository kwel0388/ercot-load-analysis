# ERCOT Load & Temperature Analysis — 2025

Analyses the relationship between temperature and electricity demand across ERCOT's 8 weather zones using 2025 hourly data.

## What it does
- Merges ERCOT native load data with ASOS weather station data from 178 Texas stations
- Assigns stations to ERCOT zones via county boundary shapefiles
- Calculate Cooling Degree Hours (CDH) and Heating Degree Hours (HDH) from hourly temperature
- Runs OLS regression of zone load on CDH, HDH, hour-of-day fixed effects, and weekend indicator — separately for all 8 zones

## Key findings
- Temperature and time-of-day explain 74–87% of load variance in weather-sensitive zones (R² = 0.741–0.868)
- NCENT is the most temperature-sensitive zone at 385 MW per cooling degree-hour
- FWEST shows weak temperature dependence (R² = 0.36)

## Data sources
- **ERCOT Native Load:** [ercot.com/gridinfo/load/load_hist](http://www.ercot.com/gridinfo/load/load_hist)
- **Weather:** Iowa Environmental Mesonet ASOS — [https://mesonet.agron.iastate.edu/request/download.phtml?network=TX_ASOS](https://mesonet.agron.iastate.edu/request/download.phtml?network=TX_ASOS)
- **County boundaries:** TxDOT [https://gis-txdot.opendata.arcgis.com/datasets/TXDOT::texas-county-boundaries-detailed](https://gis-txdot.opendata.arcgis.com/datasets/TXDOT::texas-county-boundaries-detailed)

## Files
- `ercot_analysis.py`
- `ercot_output/zone_summary_stats.csv` — descriptive stats by zone
- `ercot_output/regression_results.csv` — OLS results by zone
