import folium
import pandas as pd
import json

# -----------------------------
# STEP 1: Load dataset
# -----------------------------
df = pd.read_csv("01_District_wise_crimes_committed_IPC_2001_2012.csv")

# Clean column names
df.columns = df.columns.str.strip().str.upper()

print("Columns:", df.columns.tolist())

# -----------------------------
# STEP 2: Auto-detect state column
# -----------------------------
state_col = [col for col in df.columns if "STATE" in col][0]
print("Using state column:", state_col)

# FIX: Remove aggregated TOTAL rows to avoid double-counting every state
df = df[df["DISTRICT"].str.upper() != "TOTAL"]

# -----------------------------
# STEP 3: Aggregate data
# -----------------------------
crime_data = df.groupby(state_col).sum(numeric_only=True)
crime_data["Total_Crime"] = crime_data.sum(axis=1)
crime_data = crime_data.reset_index()

# Rename for map
crime_data.rename(columns={state_col: "State"}, inplace=True)

# -----------------------------
# STEP 4: Fix state name mismatch
# -----------------------------
state_mapping = {
    "A & N ISLANDS": "Andaman and Nicobar Islands",
    "DELHI UT": "Delhi",
    "D & N HAVELI": "Dadra and Nagar Haveli",
    "DAMAN & DIU": "Daman and Diu",
    "UTTARANCHAL": "Uttarakhand",
    "ORISSA": "Odisha"
}
crime_data["State"] = crime_data["State"].replace(state_mapping)

# -----------------------------
# STEP 5: Create Safety Score (normalised 0–100, higher = safer)
# FIX: Use min-max normalisation so score never goes negative
# -----------------------------
min_crime = crime_data["Total_Crime"].min()
max_crime = crime_data["Total_Crime"].max()
crime_data["Safety_Score"] = 100 * (1 - (crime_data["Total_Crime"] - min_crime) / (max_crime - min_crime))

# -----------------------------
# STEP 6: Load GeoJSON
# -----------------------------
with open("india_states.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# -----------------------------
# STEP 7: Create map
# -----------------------------
m = folium.Map(
    location=[22.5, 78.9],
    zoom_start=5,
    tiles="cartodb dark_matter"
)

# -----------------------------
# STEP 8: Choropleth
# -----------------------------
folium.Choropleth(
    geo_data=geojson_data,
    data=crime_data,
    columns=["State", "Safety_Score"],
    key_on="feature.properties.ST_NM",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name="Safety Score (0 = most crime, 100 = least crime)"
).add_to(m)

# -----------------------------
# STEP 9: Tooltip
# -----------------------------
folium.GeoJson(
    geojson_data,
    tooltip=folium.GeoJsonTooltip(
        fields=["ST_NM"],
        aliases=["State:"]
    )
).add_to(m)

# -----------------------------
# STEP 10: Save output
# -----------------------------
m.save("india_crime_real_map.html")
print("Done! Open india_crime_real_map.html")
