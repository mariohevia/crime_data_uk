
from crime_data_fetch import get_crime_street_level_point, get_lat_long_from_postcode, list_crimes_to_list_coordinates
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from collections import Counter

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Click on the map or enter a postcode to view street-level crime data.")

# Initialize session state
if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = None
if "crime_data" not in st.session_state:
    st.session_state["crime_data"] = []

# Create base map
m = folium.Map(location=[55.3781, -3.4360], zoom_start=6)

# Display map and capture clicks
map_data = st_folium(m, height=500, width=700, key="main_map")
if map_data and "last_clicked" in map_data:
    st.session_state["selected_location"] = map_data["last_clicked"]

# Display selected location
if st.session_state["selected_location"]:
    lat, lon = st.session_state["selected_location"]["lat"], st.session_state["selected_location"]["lng"]
    st.write(f"Selected location: {lat:.6f}, {lon:.6f}")

    # Button to fetch crime data
    if st.button("Get Crime Data for Selected Point"):
        st.session_state["crime_data"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))

# Postcode input
postcode = st.text_input("Enter a postcode:")
if st.button("Get Crime Data from Postcode"):
    lat, lon = get_lat_long_from_postcode(postcode)
    st.session_state["selected_location"] = {"lat": lat, "lng": lon}
    st.session_state["crime_data"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))
    st.write(f"Postcode location: {lat:.6f}, {lon:.6f}")

# Re-render map with selected location and crime data
m = folium.Map(location=[55.3781, -3.4360], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)

# Plot clicked location
if st.session_state["selected_location"]:
    folium.Marker(
        [st.session_state["selected_location"]["lat"], st.session_state["selected_location"]["lng"]],
        popup="Selected Location",
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Count and plot crime occurrences
crime_counts = Counter(st.session_state["crime_data"])
for (lat, lon), count in crime_counts.items():
    folium.Circle(
        location=[lat, lon],
        radius=200 + count * 50,  # Scale size based on occurrences
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.6,
        popup=f"Crimes: {count}"
    ).add_to(m)

# Display updated map with a unique key
st_folium(m, height=500, width=700, key="updated_map")
