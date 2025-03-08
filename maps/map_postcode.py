from utils.crime_data_fetch import get_crime_street_level_point, get_lat_long_from_postcode, list_crimes_to_df
from utils.map_utils import color_function, add_crime_counts_to_map
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Enter a postcode to view street-level crime data.")

# Initialize session state
if "selected_location_postcode" not in st.session_state:
    st.session_state["selected_location_postcode"] = None
if "crime_data_postcode" not in st.session_state:
    st.session_state["crime_data_postcode"] = None

# Create base map
center = [52, -1]
zoom = 7
map_postcode = folium.Map(location=center, zoom_start=zoom)
fg = folium.FeatureGroup(name="Marker")

# Postcode input
postcode = st.text_input("Enter a postcode:",label_visibility="collapsed")
if st.button("Get Crime Data"):
    correct_pc, lat, lon, error = get_lat_long_from_postcode(postcode)
    st.session_state["selected_location_postcode"] = {"correct_pc":correct_pc, "lat": lat, "lng": lon, "error": error}

# Display selected location
if st.session_state["selected_location_postcode"]:
    lat, lon = st.session_state["selected_location_postcode"]["lat"], st.session_state["selected_location_postcode"]["lng"]
    if st.session_state["selected_location_postcode"]["correct_pc"]:
        st.write(f"Selected location: {lat:.6f}, {lon:.6f}")
    else:
        st.write(f"Selected location: {st.session_state['selected_location_postcode']['error']}")
    fg.add_child(
        folium.Marker(
            [lat, lon], tooltip="Selected location"
        ))
    center = [lat,lon]
    zoom = 13
    st.session_state["crime_data_postcode"] = list_crimes_to_df(get_crime_street_level_point(lat, lon))

    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["crime_data_postcode"], fg)
else: 
    st.write("Selected location: ")

# Display map
map_data = st_folium(map_postcode, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_postcode',
    center=center)