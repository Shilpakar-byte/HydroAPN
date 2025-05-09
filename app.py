import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from utils import load_hydropower_data, load_rainfall_data, load_salient_features

# App title
st.title("Hydropower Project Explorer")

# Load hydropower points
hydro_df = load_hydropower_data("hydropower_points/hydropower_points.csv")

# Sidebar selection
project_names = hydro_df["Name"].unique()
selected_project = st.sidebar.selectbox("Select a Hydropower Project", project_names)

# Get project info
project = hydro_df[hydro_df["Name"] == selected_project].iloc[0]
lat, lon = project["Latitude"], project["Longitude"]
st.subheader(f"📍 {selected_project.replace('_', ' ')}")

# Show map
m = folium.Map(location=[lat, lon], zoom_start=11)
folium.Marker([lat, lon], popup=f"{selected_project}", icon=folium.Icon(color='blue')).add_to(m)
st_data = st_folium(m, width=700)

# Show salient features
st.markdown("### Salient Features")
try:
    salient_df = load_salient_features(f"data/{selected_project}.csv")
    st.dataframe(salient_df)
except FileNotFoundError:
    st.warning("Salient feature file not found for this project.")

# Show rainfall plot
st.markdown("### Rainfall Data")
rainfall_df = load_rainfall_data("rainfall/rainfall_data_2024.csv")

# Process date
rainfall_df["Date"] = pd.to_datetime(rainfall_df[["year", "month", "day"]])
rainfall_df.set_index("Date", inplace=True)

# Plot
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(rainfall_df.index, rainfall_df["Precipitation_mm_per_day"], label="Rainfall (mm/day)", color='blue')
ax.set_title("Rainfall Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Precipitation (mm)")
ax.grid(True)
st.pyplot(fig)
