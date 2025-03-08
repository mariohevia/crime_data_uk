from utils.crime_data_fetch import get_crime_street_level_area, list_crimes_to_df
from utils.map_utils import color_function, add_crime_counts_to_map
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Create polygons with the map tools to view street-level crime data.")

# Initialize session state
if "selected_location_area" not in st.session_state:
    st.session_state["selected_location_area"] = None
if "crime_data_area" not in st.session_state:
    st.session_state["crime_data_area"] = None

# Create base map
center = [52, -1]
zoom = 7
map_area = folium.Map(location=center, zoom_start=zoom)
fg = folium.FeatureGroup(name="Marker")

draw_options={
    'polyline':False,
    'rectangle':False,
    'circle':False,
    'circlemarker':False,
    'marker':False,
}
Draw(export=False, draw_options=draw_options).add_to(map_area)

if 'map_area' in st.session_state:
    if "last_active_drawing" in st.session_state['map_area'] and st.session_state['map_area']["last_active_drawing"] != None:
        coordinates = st.session_state['map_area']["last_active_drawing"]["geometry"]["coordinates"][0]
        st.session_state["selected_location_area"] = coordinates

# Display selected location
if st.session_state["selected_location_area"]:
    # Extract longitudes and latitudes separately
    lons, lats = zip(*st.session_state["selected_location_area"])
    # Compute the center
    lon = (min(lons) + max(lons)) / 2
    lat = (min(lats) + max(lats)) / 2
    st.write(f"Selected location: {lat:.6f}, {lon:.6f}")
    center = [lat,lon]
    zoom = 13
    st.session_state["crime_data_area"] = list_crimes_to_df(get_crime_street_level_area(st.session_state["selected_location_area"]))

    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["crime_data_area"], fg)
else: 
    st.write("Selected location: ")

# Display map
map_data = st_folium(map_area, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_area',
    center=center)