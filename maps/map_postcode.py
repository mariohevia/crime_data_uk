from utils.crime_data_fetch import get_crime_street_level_point, get_postcode_info_from_postcode, list_crimes_to_df
from utils.map_utils import color_function, add_crime_counts_to_map, write_selected_location_in_st
from utils.data_utils import add_pills_filter_df
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
col1, col2 = st.columns(2)
with col1:
    postcode = st.text_input("Enter a postcode:",label_visibility="collapsed")
with col2:
    if st.button("Get Crime Data"):
        f_error, error, postcode_info  = get_postcode_info_from_postcode(postcode)
        st.session_state["selected_location_postcode"] = {"f_error":f_error, "error": error, "postcode_info": postcode_info}

# Display selected location
if st.session_state["selected_location_postcode"]:
    lat, lon = (
        st.session_state["selected_location_postcode"]["postcode_info"]["latitude"], 
        st.session_state["selected_location_postcode"]["postcode_info"]["longitude"]
    )
    list_crimes, status_code = get_crime_street_level_point(lat, lon)
    st.session_state["crime_data_postcode"] = list_crimes_to_df(list_crimes)
    write_selected_location_in_st(
        status_code=status_code, 
        lat = lat,
        lon = lon,
        **st.session_state["selected_location_postcode"]
    )
    fg.add_child(
        folium.Marker(
            [lat, lon], tooltip="Selected location"
        ))
    center = [lat,lon]
    zoom = 13

    # Filters the data to include only the crimes with certain categories
    st.session_state["crime_data_postcode"] = add_pills_filter_df(st.session_state["crime_data_postcode"])
    # Count and plot crime occurrences
    add_crime_counts_to_map(st.session_state["crime_data_postcode"], fg)
else: 
    st.subheader("Selected location")
    # Shows the pills
    add_pills_filter_df()

# Display map
map_data = st_folium(map_postcode, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_postcode',
    returned_objects=[],
    center=center)