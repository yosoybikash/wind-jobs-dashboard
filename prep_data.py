# prep_data.py
import geopandas as gpd
import pandas as pd
import numpy as np

# 1) Read the US county shapefile (adjust the path if your folder name is different)
us_county_shp = gpd.read_file('cb_2018_us_county_500k/cb_2018_us_county_500k.shp')

# 2) Remove empty rows just in case
us_county_shp = us_county_shp.dropna(subset=['STATEFP'])

# 3) Filter to the four states (KY=21, OH=39, PA=42, WV=54)
state_fp = [21, 39, 42, 54]
us_county_shp['STATEFP'] = us_county_shp['STATEFP'].astype(int)
appalachian_shp = us_county_shp[us_county_shp['STATEFP'].isin(state_fp)].copy()

# 4) Read Michael's CSV
county_jobs_michael = pd.read_csv('county_jobs_michael.csv')

# 5) Rename columns to NAICS names (matching your earlier notebook)
county_jobs_michael = county_jobs_michael.rename(columns={
    'Plastics and Rubber Products Manufacturing': 'NAICS 326',
    'Primary Metal Manufacturing': 'NAICS 331',
    'Fabricated Metal Product Manufacturing': 'NAICS 332',
    'Machinery Manufacturing': 'NAICS 333',
    'Electrical Equipment, Appliance and Component Manufacturing': 'NAICS 335',
    'Subsector': 'County'
})

# 6) Drop first row if it’s a header-like row (you did this before)
county_jobs_michael = county_jobs_michael.drop(0)

# 7) Map state abbreviations to FIPS codes for the join
state_map = {"KY": 21, "OH": 39, "PA": 42, "WV": 54}
county_jobs_michael['StateID'] = county_jobs_michael['State'].map(state_map).astype(int)

# 8) Filter to Appalachia == 'Yes' (as in your notebook)
county_jobs_michael = county_jobs_michael[county_jobs_michael['Appalachia'] == 'Yes'].copy()

# 9) Merge shapefile with jobs table
merged_df = appalachian_shp.merge(
    county_jobs_michael,
    left_on=["STATEFP", "NAME"],
    right_on=["StateID", "County"],
    how="inner"
)

# 10) Ensure CRS is WGS84 (EPSG:4326) for Folium/Leaflet
if merged_df.crs is None:
    # Many Census files are EPSG:4269; set and reproject if needed
    merged_df = merged_df.set_crs(epsg=4269, allow_override=True).to_crs(epsg=4326)
else:
    merged_df = merged_df.to_crs(epsg=4326)

# 11) Save a clean GeoJSON for the app
merged_df.to_file("data/appalachia.geojson", driver="GeoJSON")
print("✅ Wrote data/appalachia.geojson with", len(merged_df), "counties.")
