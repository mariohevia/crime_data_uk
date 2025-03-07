
from crime_data_fetch import get_crime_street_level_point, get_lat_long_from_postcode, list_crimes_to_list_coordinates
import streamlit as st
import folium
from streamlit_folium import st_folium
from collections import Counter

map_click_page = st.Page(
    "maps/map_click.py", title="Clickable Crime Map", icon=":material/location_on:", default=True
)
map_postcode_page = st.Page(
    "maps/map_postcode.py", title="Postcode Crime Map", icon=":material/approval:", default=False
)
map_area_page = st.Page(
    "maps/map_area.py", title="Area Crime Map", icon=":material/polyline:", default=False
)

pg = st.navigation(
        {
            "Interactive Crime Maps": [map_click_page, map_postcode_page, map_area_page],
        }
    )
    
pg.run()