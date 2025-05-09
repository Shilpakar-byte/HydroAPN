import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from utils import load_hydropower_data, load_rainfall_data, load_salient_features

# App title
st.title("Hydropower Project Explorer")

# Load hydropower points
hydro_df = load_hydropower_data("hydropower_points/Hydropower_list.csv")

# Sidebar selection
project_names = hydro_df["Name"].unique()
selected_project = st.sidebar.selectbox("Select a Hydropower Project", project_names)

# Display all points on the map
st.markdown("### All Hydropower Projects")

# Define the center of the map
m = folium.Map(location=[27.7, 85.3], zoom_start=8)

# Add dynamic small color-coded markers
for _, project in hydro_df.iterrows():
    lat, lon = project["Latitude"], project["Longitude"]
    project_name = project["Name"]
    license_type = project["License Type"]

    # Assign color based on license type
    if license_type == "Survey":
        marker_color = 'red'
    elif license_type == "Operation":
        marker_color = 'blue'
    else:  # Operation or others
        marker_color = 'green'

    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.8,
        popup=folium.Popup(project_name, max_width=200)
    ).add_to(m)

# Display the map
st_data = st_folium(m, width=700, height=500)

# Selected project details
st.subheader(f"📍 {selected_project.replace('_', ' ')}")

# Show salient features (inside expander)
with st.expander("📌 Salient Features"):
    try:
        salient_df = load_salient_features(f"data/{selected_project}.csv")
        st.dataframe(salient_df)
    except FileNotFoundError:
        st.warning("Salient feature file not found for this project.")

# Show rainfall data (inside expander)
with st.expander("🌧️ Rainfall Data"):
    try:
        rainfall_df = load_rainfall_data(f"rainfall/{selected_project}.csv")
        rainfall_df["Date"] = pd.to_datetime(rainfall_df[["year", "month", "day"]])
        rainfall_df.set_index("Date", inplace=True)

        st.dataframe(rainfall_df)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rainfall_df.index, rainfall_df["Precipitation_mm_per_day"], label="Rainfall (mm/day)", color='blue')
        ax.set_title("Rainfall Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Precipitation (mm)")
        ax.grid(True)
        st.pyplot(fig)

    except FileNotFoundError:
        st.warning("Rainfall data file not found for this project.")
