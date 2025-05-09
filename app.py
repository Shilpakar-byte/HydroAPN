import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from utils import load_hydropower_data, load_rainfall_data, load_salient_features
from branca.element import Template, MacroElement

# App title
st.title("Hydropower Project Explorer")

# Load hydropower points
hydro_df = load_hydropower_data("hydropower_points/Hydropower_list.csv")

# Sidebar selection
project_names = hydro_df["Name"].unique()
selected_project = st.sidebar.selectbox("Select a Hydropower Project", project_names)

# Display all points on the map
st.markdown("### All Hydropower Projects")

# Define the main map
m = folium.Map(location=[27.7, 85.3], zoom_start=8, control_scale=True)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    name="Esri Satellite",
    overlay=False,
    control=True
).add_to(m)
folium.LayerControl().add_to(m)

# Loop through each hydropower project and add a dynamic small marker
for _, project in hydro_df.iterrows():
    lat, lon = project["Latitude"], project["Longitude"]
    project_name = project["Name"]
    license_type = project["License Type"]

    # Set marker color based on license type
    if license_type == "Survey":
        marker_color = 'red'
    elif license_type == "Construction":
        marker_color = 'blue'
    else:  # Operation or others
        marker_color = 'green'

    folium.Marker(
        [lat, lon],
        popup=project_name,
        icon=folium.Icon(color=marker_color, icon='circle')
    ).add_to(m)

# Add legend inside the map
legend_html = """
{% macro html() %}
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 160px;
    height: 120px;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
<b>License Type</b><br>
<i class="fa fa-map-marker" style="color:red"></i> Survey<br>
<i class="fa fa-map-marker" style="color:blue"></i> Construction<br>
<i class="fa fa-map-marker" style="color:green"></i> Operation<br>
</div>
{% endmacro %}
"""
legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# Show map
st_data = st_folium(m, width=900, height=600)

# Selected project details
st.markdown("### Selected Project Information")
selected_project_data = hydro_df[hydro_df["Name"] == selected_project].iloc[0]
selected_lat, selected_lon = selected_project_data["Latitude"], selected_project_data["Longitude"]

# Show zoomed-in map of selected project
m_selected = folium.Map(location=[selected_lat, selected_lon], zoom_start=11)
folium.TileLayer('Esri Satellite').add_to(m_selected)
folium.Marker(
    [selected_lat, selected_lon],
    popup=f"{selected_project}",
    icon=folium.Icon(color='blue', icon='info-sign')
).add_to(m_selected)
st_data_selected = st_folium(m_selected, width=900, height=600)

# Salient Features Section
st.markdown("### Salient Features")
try:
    salient_df = load_salient_features(f"data/{selected_project}.csv")
    st.dataframe(salient_df)
except FileNotFoundError:
    st.warning("Salient feature file not found for this project.")

# Rainfall Data Section
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
