# ERCOT Load & Temperature Analysis

This project is meant to demonstrate a simple regression analysis with ERCOT 2025 hourly load & hourly temps across TX. 

The regression analysis quanitifies how much additional load (in MW) each zone generates per degree of heat or cold beyond a 65°F baseline - after controlling for time-of-day patterns and weekend differences. 

Kel Westkaemper, May 2026

## Files
- `ercot_analysis.py` - runs the analysis
- `ercot_output/zone_summary_stats.csv` - summary statistics by zone
- `ercot_output/regression_results.csv` - OLS results by zone
- `txstations.csv` - lat/long of all ASOS tx stations
- `station_to_zone` - ASOS station to ERCOT weather zone
- `Native_Load_2025.xlsx` - ercot native load file
- `Texas_County_Boundaries_Detailed.csv` - maps all counties to ercot weather region

## Data 
- **ERCOT Native Load:** [ercot.com/gridinfo/load/load_hist](http://www.ercot.com/gridinfo/load/load_hist)
    - 8,759 hourly observations across ERCOT's 8 weather zones
    - units in MW
- **Weather:** Iowa Environmental Mesonet ASOS — [https://mesonet.agron.iastate.edu/request/download.phtml?network=TX_ASOS](https://mesonet.agron.iastate.edu/request/download.phtml?network=TX_ASOS)
    - 178 weather stations within ERCOT's coverage area
    - 927,860 temperature readings within ERCOT's coverage area
    - Num temp readings per weather zone: 
      - COAST: 84,190
      - EAST: 84,725
      - FWEST: 92,971
      - NCENT: 225,549
      - NORTH: 44,291
      - SCENT: 144,333
      - SOUTH: 142,304
      - WEST: 109,497 
- **County boundaries:** TxDOT [https://gis-txdot.opendata.arcgis.com/datasets/TXDOT::texas-county-boundaries-detailed](https://gis-txdot.opendata.arcgis.com/datasets/TXDOT::texas-county-boundaries-detailed)
  - ASOS stations were assigned to zones via point-in-polygon spatial join against county boundary shapefiles

## Summary statistics
| zone | Avg Load (MW) | Peak Load (MW) | Avg Temp (F) |	Max Temp (F)	| Min Temp (F)	| n (hours)
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | 
| COAST   | 14,752	| 23,007	| 71.8	| 96.6	| 20.5	| 8734 |
| EAST   | 1,818	| 3,697	| 68.1	| 99.1	| 16.9	| 8733 |
| FWEST | 7,477	| 8,773	| 67.1	| 102.1	| 14.1| 	8734
| NCENT	| 15,311	| 27,532	| 67.2	| 100.9	| 11.6| 	8734 |
| NORTH	| 1,690	| 2,732	| 65.9	| 99.1	| 8.3| 8734 |
| SCENT	| 8,880	| 14799	| 70.6	| 99.7	| 20.2	| 8734 |
| SOUTH	| 4,436	| 7,156	| 74.5	| 100.8	| 23.1	| 8734 | 
| WEST	| 1,385	| 2,117	| 68.2| 	101.3	| 15.5	| 8734 |

## Regression model

```
load_mw = β₀ + β₁(CDH) + β₂(HDH) + γₕ(C(hour)) + δ(is_weekend) + ε
```
- CDH = max(temp_f − 65, 0)
  - Measures heat above the 65°F baseline that drives air conditioning demand. A 90°F hour produces 25 CDH.
- HDH = max(65 − temp_f, 0)
  - Measures cold below the 65°F baseline that drives heating demand. A 40°F hour produces 25 HDH. 
- C(hour): dummy variable for each hour
  - controls for time-of-day load shape
  - hour 0 (midnight) is omitted reference category: each coeff represents MW above or below midnight at that hour, holding temperature constant
- is_weekend: binary variable, 1 = Saturday or Sunday
  - captures weekend/weekday demand differences

## Visualization
South Central Texas: Temperature Response Function
![SCENT TRF](https://github.com/kwel0388/ercot-load-analysis/blob/main/ercot_output/trf_SCENT.png?raw=true)

All Zones TRF
![TRF All Zones](https://github.com/kwel0388/ercot-load-analysis/blob/main/ercot_output/trf_all_zones.png?raw=true)

South Central Texas: Daily Load Shape (MW relative to midnight)
![SCENT hour shape](https://github.com/kwel0388/ercot-load-analysis/blob/main/ercot_output/hour_shape_SCENT.png?raw=true)
- Lowest load at ~3am, highest at ~1pm 

## Results
| zone | n_obs | r_squared | CDH_coef |	HDH_coef	| weekend_coef
| -------- | -------- | -------- | -------- | -------- | -------- |
| COAST	| 8734	| 0.8684	| 320.78	| 110.01	| -577.63| 
| EAST	| 8733	| 0.7407	| 41.83	| 27.05	| -79.11 |
| FWEST	| 8734	| 0.3592	| 18.11	| -4.9	| 79.72 |
| NCENT	| 8734	| 0.7646	| 384.78	| 182.06	| -739.74 |
| NORTH	| 8734	| 0.5946	| 31.54	| 12.15	| -10.47 |
| SCENT	| 8734	| 0.8007	| 210.35	| 101.89	| -313.44 |
| SOUTH	| 8734	| 0.788	| 83.34	| 52.44	| -93.85 |
| WEST	| 8734	| 0.6446	| 21.81	| 11.77	| -20.83 |

The p-value on each coefficient was 0.0000, except: 
  - NORTH weekend_coeff: p=0.0302

How to interpret: 
- r_squared: what percentage of this zone's load is explained by (1) temperature, (2) time of day, and (3) weekday vs. weekend?
- CDH_coef: for every one degree of heat above 65°F, how many additional MW does this zone use?
- HDH_coef: for every one degree of cold below 65°F, how many additional MW does this zone use?
- weekend_coef: compared to a weekday, how many MW does this zone use differently on a Saturday or Sunday, holding temperature constant?


## Key findings
- Temperature and time-of-day explain the majority of load variance in most zones (R² = 0.59 - 0.87)
- FWEST shows weak temperature dependence (R² = 0.36)
- Notably, FWEST has a small negative HDH_coeff of 4.9 MW per degree-hour below 65°F (p=0.0000), suggesting that colder temperatures are associated with slightly less load in the Far West
- FWEST also is the only zone with a positive weekend coeff, suggesting load is higher on the weekends
- NCENT is the most temperature-sensitive zone at 385 MW per CDH & 182 MW per HDH
- CDH coefficient > HDH coefficient for each zone, suggesting Texas uses much more electricity fighting heat than fighting cold

  ## Limitations
- This was only done over a few days, so there's lots of possible analysis left to do!
- The CDH/HDH framework assumes a linear load response above and below 65°F
- Future analysis could add more weather variables such as dew point temperature as a predictor, test season-specific models, and dive deeper into FWEST's load responses