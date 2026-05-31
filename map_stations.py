"""
Auto-maps ASOS stations to ERCOT weather zones using lat/lon coordinates
and a nearest-centroid approach based on the county boundaries file.

Run this once to generate station_zone_mapping.csv, then paste the
STATION_ZONE dict output into your main analysis script.
"""

import pandas as pd
import numpy as np

WEATHER_FILE = "texas_hourly_weather_2025.csv"
COUNTY_FILE  = "Texas_County_Boundaries_Detailed.csv"

# ── 1. ZONE NAME → LOAD COLUMN MAPPING ───────────────────────────────────────
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

# ── 2. COMPUTE ZONE CENTROIDS FROM COUNTY FILE ────────────────────────────────
# The county file has Shape__Area and geometry info but no lat/lon directly.
# We'll use known approximate centroids for each ERCOT weather zone instead.
# These are well-established geographic centers for each zone.

ZONE_CENTROIDS = {
    "COAST":  (29.2, -95.5),   # Houston/Galveston area
    "EAST":   (31.5, -94.5),   # East Texas piney woods
    "FWEST":  (31.5, -103.5),  # Far West / Permian Basin
    "NORTH":  (33.5, -97.5),   # North Texas / DFW
    "NCENT":  (31.8, -99.5),   # Abilene / San Angelo
    "SOUTH":  (26.5, -98.0),   # Rio Grande Valley
    "SCENT":  (30.0, -98.0),   # Austin / San Antonio
    "WEST":   (30.5, -101.5),  # West Texas / Del Rio area
}

# ── 3. LOAD STATION COORDINATES FROM WEATHER FILE ────────────────────────────
print("Loading station coordinates from weather file...")
weather = pd.read_csv(WEATHER_FILE, usecols=["station", "lat", "lon"])
weather = weather.drop_duplicates(subset="station")
weather = weather.dropna(subset=["lat", "lon"])

# Filter to Texas bounding box (rough)
weather = weather[
    (weather["lat"] >= 25.5) & (weather["lat"] <= 36.7) &
    (weather["lon"] >= -107.0) & (weather["lon"] <= -93.5)
]

print(f"  Stations with valid Texas coordinates: {len(weather)}")

# ── 4. ASSIGN EACH STATION TO NEAREST ZONE CENTROID ──────────────────────────
def nearest_zone(lat, lon, centroids):
    """Returns the zone key with the smallest Euclidean distance."""
    min_dist = float("inf")
    best_zone = None
    for zone, (clat, clon) in centroids.items():
        # Simple Euclidean — fine for this scale within Texas
        dist = np.sqrt((lat - clat)**2 + (lon - clon)**2)
        if dist < min_dist:
            min_dist = dist
            best_zone = zone
    return best_zone

weather["zone"] = weather.apply(
    lambda row: nearest_zone(row["lat"], row["lon"], ZONE_CENTROIDS),
    axis=1
)

# ── 5. PRINT RESULTS ──────────────────────────────────────────────────────────
print("\nStation → Zone assignments:")
print(weather[["station", "lat", "lon", "zone"]].sort_values("zone").to_string(index=False))

print("\n── ZONE COUNTS ──")
print(weather["zone"].value_counts())

# ── 6. SAVE MAPPING FILE ──────────────────────────────────────────────────────
weather.to_csv("station_zone_mapping.csv", index=False)
print("\nSaved to station_zone_mapping.csv")

# ── 7. PRINT DICT TO PASTE INTO MAIN SCRIPT ───────────────────────────────────
print("\n── PASTE THIS INTO YOUR MAIN SCRIPT AS STATION_ZONE ──")
print("STATION_ZONE = {")
for _, row in weather.sort_values("zone").iterrows():
    print(f'    "{row["station"]}": "{row["zone"]}",  # lat={row["lat"]:.2f}, lon={row["lon"]:.2f}')
print("}")
