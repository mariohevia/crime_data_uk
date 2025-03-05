
from crime_data_fetch import get_crime_street_level_point, get_lat_long_from_postcode, list_crimes_to_list_coordinates
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Draw
from collections import Counter

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Click on the map or enter a postcode to view street-level crime data.")
# st.write(st.session_state)

# Initialize session state
if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = None
if "crime_data" not in st.session_state:
    st.session_state["crime_data"] = []

# Create base map
center = [52, -1]
m = folium.Map(location=[52, -1], zoom_start=7)
fg = folium.FeatureGroup(name="Marker")

draw_options={
    'polyline':False,
    'rectangle':False,
    'circle':False,
    'circlemarker':False,
    'marker':False,
}
Draw(export=True, draw_options=draw_options).add_to(m)

if 'map' in st.session_state:
    if "last_clicked" in st.session_state['map']:
        st.session_state["selected_location"] = st.session_state['map']["last_clicked"]

# # Display selected location
if st.session_state["selected_location"]:
    lat, lon = st.session_state["selected_location"]["lat"], st.session_state["selected_location"]["lng"]
    st.write(f"Selected location: {lat:.6f}, {lon:.6f}")
    fg.add_child(
        folium.Marker(
            [lat, lon], tooltip="Selected location"
        ))
    center = [lat,lon]

    # Button to fetch crime data
    # if st.button("Get Crime Data for Selected Point"):
    st.session_state["crime_data"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))

# Postcode input
postcode = st.text_input("Enter a postcode:")
if st.button("Get Crime Data from Postcode"):
    lat, lon = get_lat_long_from_postcode(postcode)
    st.session_state["selected_location"] = {"lat": lat, "lng": lon}
    st.session_state["crime_data"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))
    st.write(f"Postcode location: {lat:.6f}, {lon:.6f}")

# Count and plot crime occurrences
crime_counts = Counter(st.session_state["crime_data"])
for (lat, lon), count in crime_counts.items():
    fg.add_child(
        folium.Circle(
            location=[lat, lon],
            radius=2 + count * 5,  # Scale size based on occurrences
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.2,
            popup=f"Crimes: {count}"
        ))

# Display map
map_data = st_folium(m, 
    feature_group_to_add=fg,
    height=500, 
    width=700, 
    key='map',
    center=center)