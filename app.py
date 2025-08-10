# app.py
import json
import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Windmill Component Jobs — Appalachia", layout="wide")
st.title("Windmill Component Jobs — Appalachia")

st.markdown(
    "This app maps estimated jobs by NAICS industry in Appalachian counties. "
    "Select an industry below to color the counties by job counts."
)

# --- Load the prepped GeoJSON
with open("data/appalachia.geojson", "r") as f:
    geojson = json.load(f)

# --- Find available NAICS columns
props0 = geojson["features"][0]["properties"]
naics_cols = [k for k in props0.keys() if k.startswith("NAICS ")]
if not naics_cols:
    st.error("No NAICS columns found in the GeoJSON. Check your data prep.")
    st.stop()

# --- UI: which NAICS to map
choice = st.selectbox("Choose an industry (NAICS)", naics_cols, index=0)

# --- Bins/colors (same logic as your Folium snippet)
breaks = [-np.inf, 0, 50, 150, 250, 350, np.inf]
labels = ['Likely no jobs', '0-50', '50-150', '150-250', '250-350', 'More than 350']
colors = {
    'Likely no jobs': '#808080',
    '0-50': '#6baed6',
    '50-150': '#4292c6',
    '150-250': '#2ca25f',
    '250-350': '#238b45',
    'More than 350': '#006d2c'
}

def bin_value(v):
    # Convert values to bins; defaults to 'Likely no jobs' when missing/invalid
    try:
        v = float(v)
    except:
        return 'Likely no jobs'
    if v <= 0: return 'Likely no jobs'
    if v < 50: return '0-50'
    if v < 150: return '50-150'
    if v < 250: return '150-250'
    if v < 350: return '250-350'
    return 'More than 350'

# --- Add bin + color to each feature so Folium can style it
for feat in geojson["features"]:
    val = feat["properties"].get(choice, None)
    label = bin_value(val)
    feat["properties"]["job_bin"] = label
    feat["properties"]["color"] = colors.get(label, "#ffffff")

# --- Build the map
m = folium.Map(location=[39.5, -80.5], zoom_start=6)

folium.GeoJson(
    geojson,
    style_function=lambda f: {
        "fillColor": f["properties"].get("color", "#ffffff"),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["County", "State", choice, "job_bin"],
        aliases=["County:", "State:", "Jobs:", "Category:"],
        localize=True
    ),
).add_to(m)

# --- Simple legend
legend_html = f'''
<div style="position: fixed; bottom: 30px; left: 30px; border:2px solid grey; z-index:9999;
            font-size:14px; background-color:white; padding: 10px;">
  <b>{choice} — Jobs</b><br>
  {''.join(f'<i style="background:{c};width:18px;height:18px;float:left;margin-right:8px;"></i>{lbl}<br>' for lbl,c in colors.items())}
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=1100, height=650)
