import streamlit as st
from utils.crime_data_db import get_db_connection

# Store connection in session state
if "db_connection" not in st.session_state:
    st.session_state["db_connection"] = get_db_connection()

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