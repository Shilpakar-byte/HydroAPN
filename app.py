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
m = folium.Map(location=[27.7, 85.3], zoom_start=8)  # Adjust the center of the map as needed

# Loop through each hydropower project and add a smaller dynamic marker
for _, project in hydro_df.iterrows():
    lat, lon = project["Latitude"], project["Longitude"]
    project_name = project["Name"]
    license_type = project["License Type"]  # Assuming the column is named "License_Type"
    
    # Assign color based on license type
    if license_type == "Survey":
        marker_color = 'red'
    elif license_type == "Construction":
        marker_color = 'blue'
    else:  # Assuming "Operation" or others
        marker_color = 'green'
    
    folium.Marker(
        [lat, lon], 
        popup=f"{project_name}", 
        icon=folium.Icon(color=marker_color, icon_size=(10, 10))  # Set smaller icon size
    ).add_to(m)

# Display the map with all points
st_data = st_folium(m, width=700)

# Display selected project information
st.subheader(f"📍 {selected_project.replace('_', ' ')}")
selected_project_data = hydro_df[hydro_df["Name"] == selected_project].iloc[0]
selected_lat, selected_lon = selected_project_data["Latitude"], selected_project_data["Longitude"]

# Show map for selected project
m_selected = folium.Map(location=[selected_lat, selected_lon], zoom_start=11)
folium.Marker(
    [selected_lat, selected_lon], 
    popup=f"{selected_project}", 
    icon=folium.Icon(color='blue', icon_size=(10, 10))  # Set smaller icon size for selected project
).add_to(m_selected)
st_data_selected = st_folium(m_selected, width=700)

# Show salient features of the selected project
st.markdown("### Salient Features")
try:
    salient_df = load_salient_features(f"data/{selected_project}.csv")
    st.dataframe(salient_df)
except FileNotFoundError:
    st.warning("Salient feature file not found for this project.")

# Show rainfall data for the selected project
st.markdown("### Rainfall Data")
try:
    # Assuming the rainfall data is named similarly to the project (e.g., "Mathilo_Mailung_Khola_Jalvidut_Ayojana.csv")
    rainfall_df = load_rainfall_data(f"rainfall/{selected_project}.csv")

    # Process date
    rainfall_df["Date"] = pd.to_datetime(rainfall_df[["year", "month", "day"]])
    rainfall_df.set_index("Date", inplace=True)

    # Display rainfall data
    st.dataframe(rainfall_df)

    # Plot rainfall data
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rainfall_df.index, rainfall_df["Precipitation_mm_per_day"], label="Rainfall (mm/day)", color='blue')
    ax.set_title("Rainfall Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Precipitation (mm)")
    ax.grid(True)
    st.pyplot(fig)

except FileNotFoundError:
    st.warning("Rainfall data file not found for this project.")
