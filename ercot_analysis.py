"""
ERCOT Subregion Load & Temperature Analysis · 2025
Kel Westkaemper, github.com/kwel0388
Merges ERCOT hourly load data with ASOS weather station data from Iowa Environmental Mesonet,
sums to hourly average temperature per weather zone, and runs regression analysis.
"""
import pandas as pd
import numpy as np
from pathlib import Path
 
LOAD_FILE    = "Native_Load_2025.xlsx"
COUNTY_FILE  = "Texas_County_Boundaries_Detailed.csv"
WEATHER_FILE = "asos.csv"  
OUTPUT_DIR   = Path("ercot_output")
OUTPUT_DIR.mkdir(exist_ok=True) # allows folder to already exist
 
# - 1. ZONE NAME MAPPING -
ZONE_MAP = {
    "Coast":         "COAST",
    "East":          "EAST",
    "Far West":      "FWEST",
    "North":         "NORTH",
    "North Central": "NCENT",
    "Southern":      "SOUTH",
    "South Central": "SCENT",
    "West":          "WEST",
}
 
# ─ 2. STATION → ZONE MAPPING -
STATION_ZONE = {
    # Mapped using station lat/lon and county shapefile, then mapped station to weather zone using
    # county to weather zone mapping.

    # COAST
    "IAH":  "COAST",
    "MCJ":  "COAST",
    "ARM":  "COAST",
    "BYY":  "COAST",
    "TME":  "COAST",
    "AXH":  "COAST",
    "T41":  "COAST",
    "PKV":  "COAST",
    "VCT":  "COAST",
    "GLS":  "COAST",
    "PSX":  "COAST",
    "HOU":  "COAST",
    "LVJ":  "COAST",
    "CXO":  "COAST",
    "DWH":  "COAST",
    "LBX":  "COAST",
    "SGR":  "COAST",
    "EFD":  "COAST",
    # EAST
    "OSA":  "EAST",
    "LHB":  "EAST",
    "PSN":  "EAST",
    "SLR":  "EAST",
    "DKR":  "EAST",
    "F44":  "EAST",
    "CFD":  "EAST",
    "60R":  "EAST",
    "LFK":  "EAST",
    "CLL":  "EAST",
    "TYR":  "EAST",
    "OCH":  "EAST",
    "RFI":  "EAST",
    "JSO":  "EAST",
    # FAR WEST
    "MAF":  "FWEST",
    "BPG":  "FWEST",
    "PEQ":  "FWEST",
    "MDD":  "FWEST",
    "OZA":  "FWEST",
    "E38":  "FWEST",
    "E11":  "FWEST",
    "PRS":  "FWEST",
    "LUV":  "FWEST",
    "E41":  "FWEST",
    "VHN":  "FWEST",
    "E01":  "FWEST",
    "6R6":  "FWEST",
    "FST":  "FWEST",
    "ODO":  "FWEST",
    "INK":  "FWEST",
    "MRF":  "FWEST",
    # NORTH
    "SPS": "NORTH",
    "F05": "NORTH",
    "CWC": "NORTH",
    "0F2": "NORTH",
    "F00": "NORTH",
    "GYI": "NORTH",
    "CDS": "NORTH",
    "PRX": "NORTH",
    "SHP": "NORTH",
    "BQX": "NORTH",
    # NORTH CENTRAL
    "TPL": "NCENT",
    "GRK": "NCENT",
    "HLR": "NCENT",
    "ILE": "NCENT",
    "GZN": "NCENT",
    "ACT":  "NCENT",
    "DFW":  "NCENT",
    "GVT":  "NCENT",
    "XBP":  "NCENT",
    "ETN":  "NCENT",
    "LNC":  "NCENT",
    "GDJ":  "NCENT",
    "CPT":  "NCENT",
    "GPM":  "NCENT",
    "INJ":  "NCENT",
    "JWY":  "NCENT",
    "LUD":  "NCENT",
    "MKN":  "NCENT",
    "MNZ":  "NCENT",
    "BKD":  "NCENT",
    "RPH":  "NCENT",
    "GOP":  "NCENT",
    "SEP":  "NCENT",
    "BWD":  "NCENT",
    "F46":  "NCENT",
    "LXY":  "NCENT",
    "6P9":  "NCENT",
    "ADS":  "NCENT",
    "HQZ":  "NCENT",
    "NFW":  "NCENT",
    "GKY":  "NCENT",
    "DAL":  "NCENT",
    "FTW":  "NCENT",
    "MWL":  "NCENT",
    "RBD":  "NCENT",
    "CRS":  "NCENT",
    "TKI":  "NCENT",
    "AFW":  "NCENT",
    "DTO":  "NCENT",
    "TRL":  "NCENT",
    "CNW":  "NCENT",
    "FWS":  "NCENT",
    "PWG":  "NCENT",
    # SOUTH
    "BRO":  "SOUTH",
    "CRP":  "SOUTH",
    "BEA":  "SOUTH",
    "BKS":  "SOUTH",
    "RBO":  "SOUTH",
    "PEZ":  "SOUTH",
    "FTN":  "SOUTH",
    "CZT":  "SOUTH",
    "5T9":  "SOUTH",
    "IKG":  "SOUTH",
    "TXW":  "SOUTH",
    "T69":  "SOUTH",
    "8T6": "SOUTH",
    "TFP": "SOUTH",
    "T65": "SOUTH",
    "PIL": "SOUTH",
    "HRL": "SOUTH",
    "ALI": "SOUTH",
    "COT": "SOUTH",
    "MFE": "SOUTH",
    "RKP": "SOUTH",
    "LRD": "SOUTH",
    "NOG": "SOUTH",
    "NGP": "SOUTH",
    "NQI": "SOUTH",
    "APY": "SOUTH",
    "EBG": "SOUTH",
    "HBV": "SOUTH",
    # SOUTH CENTRAL
    "SAT":  "SCENT",
    "RYW":  "SCENT",
    "GYB":  "SCENT",
    "CVB":  "SCENT",
    "5C1":  "SCENT",
    "EDC":  "SCENT",
    "11R":  "SCENT",
    "RWV":  "SCENT",
    "3T5":  "SCENT",
    "T35":  "SCENT",
    "T20":  "SCENT",
    "66R":  "SCENT",
    "ELA":  "SCENT",
    "2R9":  "SCENT",
    "T74":  "SCENT",
    "T89":  "SCENT",
    "HDO":  "SCENT",
    "BAZ":  "SCENT",
    "ATT":  "SCENT",
    "BMQ":  "SCENT",
    "SSF":  "SCENT",
    "AUS":  "SCENT",
    "RND":  "SCENT",
    "SEQ":  "SCENT",
    "SKF":  "SCENT",
    "GTU":  "SCENT",
    "HYI":  "SCENT",
    "BSM":  "SCENT",
    # WEST
    "JCT":  "WEST",
    "SJT":  "WEST",
    "AQO":  "WEST",
    "ERV":  "WEST",
    "SWW":  "WEST",
    "SNK":  "WEST",
    "COM":  "WEST",
    "BBD":  "WEST",
    "ECU":  "WEST",
    "DZB":  "WEST",
    "SOA":  "WEST",
    "T82":  "WEST",
    "UVA":  "WEST",
    "81R":  "WEST",
    "ABI":  "WEST",
    "DRT":  "WEST",
    "DLF":  "WEST",
    "DYS":  "WEST",
    "T70":  "WEST",
    "LZZ":  "WEST"
}
 
# ─ 3. LOAD DATA -
print("Loading ERCOT load data...")
load = pd.read_excel(LOAD_FILE)
load = load.drop(columns=["Month"], errors="ignore")
load["Hour Ending"] = load["Hour Ending"].str.strip()

 # Handle "24:00" as midnight EOD by rolling to next day at "00:00"
mask = load["Hour Ending"].str.endswith("24:00").fillna(False).infer_objects(copy=False)
load.loc[mask, "Hour Ending"] = (
    pd.to_datetime(
        load.loc[mask, "Hour Ending"].str.replace("24:00", "00:00"),
        format="%m/%d/%Y %H:%M"
    ) + pd.Timedelta(days=1)
).dt.strftime("%m/%d/%Y %H:%M")

 # Convert text timestamps to datetime, dropping any rows with invalid formats
load["datetime"] = pd.to_datetime(load["Hour Ending"].dropna(), format="%m/%d/%Y %H:%M")
load = load.dropna(subset=["datetime"])
load = load.drop(columns=["Hour Ending", "ERCOT"])
load = load.set_index("datetime")
print(f"  Load data: {len(load)} hours, zones: {load.columns.tolist()}")
 

print("\nLoading weather data...")
weather = pd.read_csv(WEATHER_FILE)
weather["datetime"] = pd.to_datetime(weather["valid"])

 # Reads the ASOS weather file. tmpf = temperature in Fahrenheit, relh = relative humidity.
weather = weather[["station", "datetime", "tmpf", "relh"]].copy()
weather["tmpf"] = pd.to_numeric(weather["tmpf"], errors="coerce")
weather["relh"] = pd.to_numeric(weather["relh"], errors="coerce")
print(f"  Weather data: {len(weather)} records, stations: {weather['station'].nunique()}")
 
#  4. MAP STATIONS TO ZONES -
print("\nMapping stations to ERCOT zones...")
weather["zone"] = weather["station"].map(STATION_ZONE) # from STATION_ZONE dict defined above
 
unmapped = weather[weather["zone"].isna()]["station"].unique()
if len(unmapped) > 0:
    print(f"  Unmapped stations: {unmapped}")
 
weather = weather[weather["zone"].notna()].copy()
print(f"  Mapped stations: {weather['station'].nunique()}")
print(f"  Zones covered: {sorted(weather['zone'].unique())}")
 
# ─ 5. AGGREGATE WEATHER TO ZONE-HOUR -
# Round weather timestamps to nearest hour to align with ERCOT data
weather["datetime_hr"] = weather["datetime"].dt.floor("h")
 
# Average temperature across all stations in a zone for each hour
zone_weather = (
    weather
    .groupby(["zone", "datetime_hr"])
    .agg(
        temp_f=("tmpf", "mean"),
        humidity=("relh", "mean"),
        station_count=("station", "nunique")
    )
    .reset_index()
)
print(f"\nZone-hour weather records: {len(zone_weather)}")
 
#  6. ENGINEER FEATURES -
print("Engineering features...")
 
# Cooling Degree Hours (CDH) — above 65°F, drives AC load
zone_weather["CDH"] = (zone_weather["temp_f"] - 65).clip(lower=0)
 
# Heating Degree Hours (HDH) — below 65°F, drives heating load
zone_weather["HDH"] = (65 - zone_weather["temp_f"]).clip(lower=0)
 
# Time features
zone_weather["hour"]       = zone_weather["datetime_hr"].dt.hour
zone_weather["month"]      = zone_weather["datetime_hr"].dt.month
zone_weather["dayofweek"]  = zone_weather["datetime_hr"].dt.dayofweek  # 0=Mon
zone_weather["is_weekend"] = zone_weather["dayofweek"].isin([5, 6]).astype(int)
 
#  7. MELT LOAD DATA & MERGE -
print("Merging load and weather data...")
 
    # reshape load data from wide to long format for merging
load_long = load.reset_index().melt(
    id_vars="datetime",
    var_name="zone",
    value_name="load_mw"
)
 
    # merge on matching zone & hour, keep only hours with both load and weather
merged = pd.merge(
    load_long,
    zone_weather,
    left_on=["datetime", "zone"],
    right_on=["datetime_hr", "zone"],
    how="inner"
)
 
print(f"  Merged records: {len(merged)}")
print(f"  Zones in merged data: {sorted(merged['zone'].unique())}")
print(f"  Date range: {merged['datetime'].min()} to {merged['datetime'].max()}")
 
# ─ 8. SUMMARY STATS BY ZONE -
print("\n SUMMARY STATS BY ZONE ─")
summary = merged.groupby("zone").agg(
    avg_load_mw    =("load_mw", "mean"),
    peak_load_mw   =("load_mw", "max"),
    avg_temp_f     =("temp_f", "mean"),
    max_temp_f     =("temp_f", "max"),
    min_temp_f     =("temp_f", "min"),
    hours_covered  =("load_mw", "count")
).round(1)
print(summary.to_string())
 
# ─ 9. REGRESSION: TEMP → LOAD BY ZONE -
print("\n─ OLS REGRESSION: LOAD ~ CDH + HDH + HOUR + WEEKEND BY ZONE ─")
 
import statsmodels.formula.api as smf
 
regression_results = []
 
for zone in sorted(merged["zone"].unique()):
    df_zone = merged[merged["zone"] == zone].copy()
    
    # Ensure correct dtypes before regression
    df_zone["load_mw"]    = pd.to_numeric(df_zone["load_mw"], errors="coerce")
    df_zone["CDH"]        = pd.to_numeric(df_zone["CDH"], errors="coerce")
    df_zone["HDH"]        = pd.to_numeric(df_zone["HDH"], errors="coerce")
    df_zone["is_weekend"] = pd.to_numeric(df_zone["is_weekend"], errors="coerce")
    df_zone["hour"]       = df_zone["hour"].astype(int)
    df_zone = df_zone.dropna(subset=["load_mw", "CDH", "HDH", "is_weekend", "hour"])

    # Simple OLS: load ~ CDH + HDH + hour dummies + weekend binary
    model = smf.ols(
        "load_mw ~ CDH + HDH + C(hour) + is_weekend",
            # CDH coeff = MW added per degree-hour of heat above 65°F
            # HDH coeff = MW added per degree-hour of cold below 65°F
            # C(hour) — dummy variables for all 24 hours, controls for daily load shape
            # is_weekend — controls for lower weekend load patterns
        data=df_zone
    ).fit()

    regression_results.append({
        "zone":        zone,
        "n_obs":       int(model.nobs),
        "r_squared":   round(model.rsquared, 4), # proportion of load variance explained (0 to 1)
        "CDH_coef":    round(model.params.get("CDH", np.nan), 2),
        "HDH_coef":    round(model.params.get("HDH", np.nan), 2),
        "weekend_coef":round(model.params.get("is_weekend", np.nan), 2),
    })

    print(f"\n{zone}: R²={model.rsquared:.3f}, n={int(model.nobs)}")
    print(f"  CDH coef: {model.params.get('CDH', 'N/A'):.2f} MW per degree-hour above 65°F")
    print(f"  HDH coef: {model.params.get('HDH', 'N/A'):.2f} MW per degree-hour below 65°F")
    print(f"  Weekend: {model.params.get('is_weekend', 'N/A'):.2f} MW (vs weekday)")

reg_df = pd.DataFrame(regression_results)
reg_df.to_csv(OUTPUT_DIR / "regression_results.csv", index=False)
print(f"\nRegression results saved to {OUTPUT_DIR}/regression_results.csv")

print("Model Summary:")
print(model.summary())
 
#  10. SAVE OUTPUTS -
merged.to_csv(OUTPUT_DIR / "merged_load_weather.csv", index=False)
summary.to_csv(OUTPUT_DIR / "zone_summary_stats.csv")
zone_weather.to_csv(OUTPUT_DIR / "zone_weather_engineered.csv", index=False)
 
print(f"\n✓ All outputs saved to ./{OUTPUT_DIR}/")


# ─ 11. PLOT RESULTS -
import matplotlib.pyplot as plt

# After your regression, generate predicted load across a temperature range
# holding hour and weekend fixed at representative values

zone = "SCENT"
df_zone = merged[merged["zone"] == zone].copy()

# Re-fit model on SCENT data
df_zone["load_mw"] = pd.to_numeric(df_zone["load_mw"], errors="coerce")
df_zone["CDH"] = pd.to_numeric(df_zone["CDH"], errors="coerce")
df_zone["HDH"] = pd.to_numeric(df_zone["HDH"], errors="coerce")
df_zone["is_weekend"] = pd.to_numeric(df_zone["is_weekend"], errors="coerce")
df_zone["hour"] = df_zone["hour"].astype(int)
df_zone = df_zone.dropna(subset=["load_mw","CDH","HDH","is_weekend","hour"])

model = smf.ols(
    "load_mw ~ CDH + HDH + C(hour) + is_weekend",
    data=df_zone
).fit()

# Generate prediction grid — sweep temp from 10°F to 110°F
# Hold hour=14 (2pm peak), weekday
temp_range = np.linspace(10, 110, 200)
pred_df = pd.DataFrame({
    "temp_f":     temp_range,
    "CDH":        np.maximum(temp_range - 65, 0),
    "HDH":        np.maximum(65 - temp_range, 0),
    "hour":       14,
    "is_weekend": 0,
})

pred_df["predicted_load"] = model.predict(pred_df)

# ─ Plot 1: Temperature response function  -
    # TRF shows how power demand changes as temperature changes
fig, ax = plt.subplots(figsize=(9, 5))

# Scatter actual data
hour_sample = df_zone[df_zone["hour"] == 14]
sample = hour_sample.sample(min(500, len(hour_sample)))
ax.scatter(sample["temp_f"], sample["load_mw"],
           alpha=0.15, s=8, color="#B5D4F4", label="Actual (2pm hours)")

# Fitted curve
ax.plot(pred_df["temp_f"], pred_df["predicted_load"],
        color="#185FA5", linewidth=2.5, label="Fitted response")

# Reference line at 65°F
ax.axvline(65, color="#888780", linestyle="--", linewidth=1, alpha=0.7)
ax.text(66, ax.get_ylim()[0] * 1.02, "65°F baseline", 
        fontsize=9, color="#888780")

ax.set_xlabel("Temperature (°F)", fontsize=11)
ax.set_ylabel("Load (MW)", fontsize=11)
ax.set_title(f"Temperature Response Function — {zone} Zone, 2pm Weekday", fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("ercot_output/trf_scent.png", dpi=150)
plt.show()

# ─ Plot 2: Compare TRF across all zones ─

fig, ax = plt.subplots(figsize=(10, 6))

colors = {
    "COAST": "#185FA5", "EAST": "#0F6E56", "FWEST": "#854F0B",
    "NCENT": "#993556", "NORTH": "#534AB7", "SCENT": "#D85A30",
    "SOUTH": "#639922", "WEST": "#888780"
}

for zone in sorted(merged["zone"].unique()):
    df_zone = merged[merged["zone"] == zone].copy()
    df_zone["load_mw"]    = pd.to_numeric(df_zone["load_mw"], errors="coerce")
    df_zone["CDH"]        = pd.to_numeric(df_zone["CDH"], errors="coerce")
    df_zone["HDH"]        = pd.to_numeric(df_zone["HDH"], errors="coerce")
    df_zone["is_weekend"] = pd.to_numeric(df_zone["is_weekend"], errors="coerce")
    df_zone["hour"]       = df_zone["hour"].astype(int)
    df_zone = df_zone.dropna(subset=["load_mw","CDH","HDH","is_weekend","hour"])

    model = smf.ols(
        "load_mw ~ CDH + HDH + C(hour) + is_weekend",
        data=df_zone
    ).fit()

    temp_range = np.linspace(20, 105, 200)
    pred_df = pd.DataFrame({
        "temp_f":     temp_range,
        "CDH":        np.maximum(temp_range - 65, 0),
        "HDH":        np.maximum(65 - temp_range, 0),
        "hour":       14,
        "is_weekend": 0,
    })
    pred_df["predicted_load"] = model.predict(pred_df)

    # Normalize to % of load at 65°F for comparability across zones
    load_at_65 = pred_df.loc[
        (pred_df["temp_f"] - 65).abs().idxmin(), "predicted_load"
    ]
    pred_df["pct_deviation"] = (
        (pred_df["predicted_load"] - load_at_65) / load_at_65 * 100
    )

    ax.plot(pred_df["temp_f"], pred_df["pct_deviation"],
            color=colors[zone], linewidth=2, label=zone)

ax.axvline(65, color="#888780", linestyle="--", linewidth=1, alpha=0.6)
ax.axhline(0,  color="#888780", linestyle="-",  linewidth=0.5, alpha=0.4)
ax.set_xlabel("Temperature (°F)", fontsize=11)
ax.set_ylabel("% deviation from load at 65°F", fontsize=11)
ax.set_title("Temperature Response Functions by ERCOT Zone — 2pm Weekday", fontsize=12)
ax.legend(fontsize=9, loc="upper center")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("ercot_output/trf_all_zones.png", dpi=150)
plt.show()

# - Plot 3: Hour-of-day load shape
    # Extract and plot the hour dummy coefficients for one zone

zone = "SCENT"
df_zone = merged[merged["zone"] == zone].copy()
model = smf.ols("load_mw ~ CDH + HDH + C(hour) + is_weekend", data=df_zone).fit()

# Extract hour coefficients — C(hour)[T.1] through C(hour)[T.23]
hour_coefs = {}
for h in range(1, 24):
    key = f"C(hour)[T.{h}]"
    if key in model.params:
        hour_coefs[h] = model.params[key]
hour_coefs[0] = 0  # reference hour

hours = sorted(hour_coefs.keys())
coefs = [hour_coefs[h] for h in hours]

fig, ax = plt.subplots(figsize=(10, 4))
ax.fill_between(hours, coefs, alpha=0.2, color="#185FA5")
ax.plot(hours, coefs, color="#185FA5", linewidth=2)
ax.axhline(0, color="#888780", linewidth=0.5)
ax.set_xlabel("Hour of day", fontsize=11)
ax.set_ylabel("MW relative to midnight", fontsize=11)
ax.set_title(f"Daily load shape — {zone} (hour fixed effects)", fontsize=12)
ax.set_xticks(range(0, 24, 2))
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"ercot_output/hour_shape_{zone}.png", dpi=150)
plt.show()

# Find the hour with the highest coefficient
peak_hour = max(hour_coefs, key=hour_coefs.get)
peak_mw = hour_coefs[peak_hour]

print(f"Peak hour: {peak_hour}:00 ({peak_hour % 12 or 12}{'am' if peak_hour < 12 else 'pm'})")
print(f"Peak MW above midnight baseline: {peak_mw:.1f} MW")

# Also find the trough
trough_hour = min(hour_coefs, key=hour_coefs.get)
trough_mw = hour_coefs[trough_hour]
print(f"Trough hour: {trough_hour}:00 ({trough_hour % 12 or 12}am)")
print(f"Trough MW relative to midnight: {trough_mw:.1f} MW")

# Full swing
print(f"Peak-to-trough range: {peak_mw - trough_mw:.1f} MW")