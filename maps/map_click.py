import utils.crime_data_fetch as api
import utils.crime_data_db as db
from utils.map_utils import color_function, add_crime_counts_to_map, write_selected_location_in_st
import utils.data_utils as dutils
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

# Display date selectors and store a list of dates in st.session_state[key+"list_crime_dates"]
dutils.add_start_end_month(key="map_click_")

# Display crimes in selected location
if st.session_state["selected_location_click"]:
    lat, lon = (
        st.session_state["selected_location_click"]["lat"], 
        st.session_state["selected_location_click"]["lng"]
    )
    if st.session_state["db_connection"] != None:
        st.session_state["crime_data_clickable"] = db.get_crime_street_level_point_dates(
            lat, 
            lon, 
            st.session_state["map_click_list_crime_dates"])
        status_code = 200
    else:
        list_crimes, status_code = api.get_crime_street_level_point_dates(
            lat, 
            lon, 
            st.session_state["map_click_list_crime_dates"])
        st.session_state["crime_data_clickable"] = api.list_crimes_to_df(list_crimes)
    f_error, error, postcode_info  = api.get_postcode_info_from_lat_long(lat, lon)
    fg.add_child(
        folium.Marker(
            [lat, lon], tooltip="Selected location"
        ))
    center = [lat,lon]
    zoom = 13

    # Filters the data to include only the crimes with certain categories
    st.session_state["filtered_crime_data_clickable"] = dutils.add_pills_filter_df(st.session_state["crime_data_clickable"])
    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["filtered_crime_data_clickable"], fg)
else: 
    # Shows the pills
    dutils.add_pills_filter_df()

# Display map
map_data = st_folium(map_click, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_click',
    returned_objects=["last_clicked"],
    center=center)

# Display selected location
if st.session_state["selected_location_click"]:
    write_selected_location_in_st(
        f_error, 
        error, 
        postcode_info, 
        lat, 
        lon, 
        status_code
    )
else:
    st.subheader("Selected location")

# Display crime statistics
if st.session_state["selected_location_click"]:
    dutils.add_area_line_plot_crime_statistics(st.session_state["filtered_crime_data_clickable"], key="map_click_")
    dutils.add_bar_plot_crime_statistics(st.session_state["filtered_crime_data_clickable"])
else:
    st.subheader("Crime statistics")