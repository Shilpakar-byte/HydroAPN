import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from utils import load_hydropower_data, load_rainfall_data, load_salient_features
from folium import Element

# App title
st.set_page_config(layout="wide")
st.title("Hydropower Project Explorer")

# Load hydropower points
hydro_df = load_hydropower_data("hydropower_points/Hydropower_list.csv")

# Sidebar selection
project_names = hydro_df["Name"].unique()
selected_project = st.sidebar.selectbox("Select a Hydropower Project", project_names)

# Display all points on the map
st.markdown("### All Hydropower Projects")

# Define the main map
m = folium.Map(location=[27.7, 85.3], zoom_start=8, control_scale=False)

# Add satellite tile
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri",
    name="Esri Satellite",
    overlay=False,
    control=True
).add_to(m)
folium.LayerControl().add_to(m)

# Add all hydropower points
for _, project in hydro_df.iterrows():
    lat, lon = project["Latitude"], project["Longitude"]
    project_name = project["Name"]
    license_type = project["License Type"]

    # Set marker color
    if license_type == "Survey":
        marker_color = 'red'
    elif license_type == "Operation":
        marker_color = 'blue'
    else:
        marker_color = 'green'

    folium.CircleMarker(
        location=[lat, lon],
        radius=4,  # Smaller size
        color=marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.9,
        popup=project_name
    ).add_to(m)

# Add legend using safe HTML
legend_html = '''
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 180px;
background-color: white;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding: 10px;
box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
<b>License Type</b><br>
<span style="color:red">&#x25CF;</span> Survey<br>
<span style="color:blue">&#x25CF;</span> Construction<br>
<span style="color:green">&#x25CF;</span> Operation<br>
</div>
'''
m.get_root().html.add_child(Element(legend_html))

# Show map (wider)
st_data = st_folium(m, width=1100, height=600)

# Selected project details
st.markdown("### Selected Project Information", unsafe_allow_html=True)
st.markdown('<div style="margin-top:-50px;"></div>', unsafe_allow_html=True)
selected_project_data = hydro_df[hydro_df["Name"] == selected_project].iloc[0]
selected_lat, selected_lon = selected_project_data["Latitude"], selected_project_data["Longitude"]

# Zoomed-in map
m_selected = folium.Map(location=[selected_lat, selected_lon], zoom_start=11)
st.markdown(f"**Coordinates:** {selected_lat:.6f}° N, {selected_lon:.6f}° E")

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri — Source: Esri, USGS, GeoEye, etc.",
    name="Esri Satellite",
    overlay=False,
    control=False
).add_to(m_selected)

folium.Marker(
    [selected_lat, selected_lon],
    popup=selected_project,
    icon=folium.Icon(color='blue', icon='info-sign')
).add_to(m_selected)

st_data_selected = st_folium(m_selected, width=1100, height=600)

# Salient Features
st.markdown("### Salient Features")
try:
    salient_df = load_salient_features(f"data/{selected_project}.csv")
    st.dataframe(salient_df)
except FileNotFoundError:
    st.warning("Salient feature file not found for this project.")

# Rainfall Data
st.markdown("### Rainfall Data")
try:
    rainfall_df = load_rainfall_data(f"rainfall/{selected_project}.csv")
    rainfall_df["Date"] = pd.to_datetime(rainfall_df[["year", "month", "day"]])
    rainfall_df.set_index("Date", inplace=True)

    st.dataframe(rainfall_df)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rainfall_df.index, rainfall_df["Precipitation_mm_per_day"], color='blue')
    ax.set_title("Rainfall Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Precipitation (mm)")
    ax.grid(True)
    st.pyplot(fig)

except FileNotFoundError:
    st.warning("Rainfall data file not found for this project.")
