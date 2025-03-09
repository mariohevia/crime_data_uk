from utils.crime_data_fetch import get_crime_street_level_area, get_postcode_info_from_lat_long, list_crimes_to_df
from utils.map_utils import color_function, add_crime_counts_to_map, write_selected_location_in_st
from utils.data_utils import add_pills_filter_df
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
    # Getting the crimes within the bounded area
    list_crimes, status_code = get_crime_street_level_area(st.session_state["selected_location_area"])
    st.session_state["crime_data_area"] = list_crimes_to_df(list_crimes)

    # Extract longitudes and latitudes separately
    lons, lats = zip(*st.session_state["selected_location_area"])
    # Compute the center
    lon = (min(lons) + max(lons)) / 2
    lat = (min(lats) + max(lats)) / 2
    f_error, error, postcode_info  = get_postcode_info_from_lat_long(lat, lon)
    write_selected_location_in_st(
        f_error, 
        error, 
        postcode_info, 
        lat, 
        lon, 
        status_code
    )
    center = [lat,lon]
    zoom = 13

    # Filters the data to include only the crimes with certain categories
    st.session_state["crime_data_area"] = add_pills_filter_df(st.session_state["crime_data_area"])
    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["crime_data_area"], fg)
else: 
    st.subheader("Selected location")
    # Shows the pills
    add_pills_filter_df()

# Display map
map_data = st_folium(map_area, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_area',
    returned_objects=["last_active_drawing"],
    center=center)