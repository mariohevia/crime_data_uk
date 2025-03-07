from crime_data_fetch import get_crime_street_level_point, get_lat_long_from_postcode, list_crimes_to_list_coordinates
import streamlit as st
import folium
from streamlit_folium import st_folium
from collections import Counter

def color_function(value):
    """Maps a value from 0 (green) to 25 (yellow) to 50+ (red) with gradient shades."""
    
    # Define color stops in RGB
    color_stops = [(0, (0, 128, 0)),      # Green
                   (25, (255, 255, 0)),   # Yellow
                   (50, (255, 0, 0))]     # Red

    # Find which segment the value falls into
    for i in range(len(color_stops) - 1):
        (x1, c1), (x2, c2) = color_stops[i], color_stops[i + 1]
        if value <= x2:
            # Linear interpolation between the two colors
            ratio = (value - x1) / (x2 - x1)
            interpolated_color = tuple(int((1 - ratio) * c1[j] + ratio * c2[j]) for j in range(3))
            return "#{:02x}{:02x}{:02x}".format(*interpolated_color)

    return "#ff0000"  # Red for values above 50

# Streamlit UI
st.title("UK Crime Data Explorer")
st.write("Enter a postcode to view street-level crime data.")

# Initialize session state
if "selected_location_postcode" not in st.session_state:
    st.session_state["selected_location_postcode"] = None
if "crime_data_postcode" not in st.session_state:
    st.session_state["crime_data_postcode"] = []

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
    st.session_state["crime_data_postcode"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))

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
    st.session_state["crime_data_postcode"] = list_crimes_to_list_coordinates(get_crime_street_level_point(lat, lon))
else: 
    st.write("Selected location: ")

# Count and plot crime occurrences
crime_counts = Counter(st.session_state["crime_data_postcode"])
for (lat, lon), count in crime_counts.items():
    fg.add_child(
        folium.Circle(
            location=[lat, lon],
            radius=3 + count * 2,  # Scale size based on occurrences
            color=color_function(count),
            # stroke=False,
            fill=True,
            fill_color=color_function(count),
            fill_opacity=0.6,
            tooltip=f"Crimes: {count}"
        ))

# Display map
map_data = st_folium(map_postcode, 
    feature_group_to_add=fg,
    zoom=zoom,
    height=500, 
    width=700, 
    key='map_postcode',
    center=center)