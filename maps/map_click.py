from utils.crime_data_fetch import get_crime_street_level_point, list_crimes_to_df
from utils.map_utils import color_function, add_crime_counts_to_map
from utils.data_utils import add_pills_filter_df
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Click on the map to view street-level crime data.")

# Initialize session state
if "selected_location_click" not in st.session_state:
    st.session_state["selected_location_click"] = None
if "crime_data_clickable" not in st.session_state:
    st.session_state["crime_data_clickable"] = None

# Create base map
center = [52, -1]
zoom = 7
map_click = folium.Map(location=center, zoom_start=zoom)
fg = folium.FeatureGroup(name="Marker")

if 'map_click' in st.session_state:
    if "last_clicked" in st.session_state['map_click'] and st.session_state['map_click']["last_clicked"] != None:
        st.session_state["selected_location_click"] = st.session_state['map_click']["last_clicked"]

# Display selected location
if st.session_state["selected_location_click"]:
    lat, lon = st.session_state["selected_location_click"]["lat"], st.session_state["selected_location_click"]["lng"]
    st.write(f"Selected location: {lat:.6f}, {lon:.6f}")
    fg.add_child(
        folium.Marker(
            [lat, lon], tooltip="Selected location"
        ))
    center = [lat,lon]
    zoom = 13
    st.session_state["crime_data_clickable"] = list_crimes_to_df(get_crime_street_level_point(lat, lon))

    # Filters the data to include only the crimes with certain categories
    st.session_state["crime_data_clickable"] = add_pills_filter_df(st.session_state["crime_data_clickable"])
    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["crime_data_clickable"], fg)
else: 
    st.write("Selected location: ")
    # Shows the pills
    add_pills_filter_df()

# Display map
map_data = st_folium(map_click, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_click',
    center=center)