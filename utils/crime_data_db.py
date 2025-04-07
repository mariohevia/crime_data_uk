import pandas as pd
import streamlit as st
import psycopg2
import os
from datetime import date
import time

# TODO: Handle what happens if the database breaks in the middle of a run.
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT")
        )
        return conn
    except Exception as e:
        # st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl='30d',max_entries=10000,show_spinner=False)
def get_availability():
    try:
        with st.session_state["db_connection"].cursor() as cur:
            # TODO: The code below is slower but it might be worth to put it as a MATERIALIZED VIEW
            # cur.execute("SELECT DISTINCT TO_CHAR(month, 'YYYY-MM') FROM crimes ORDER BY 1;")
            # available_dates = [row[0] for row in cur.fetchall()]
            cur.execute("SELECT DISTINCT DATE_TRUNC('month', month)::DATE FROM crimes ORDER BY 1;")
            available_dates = [row[0].strftime("%Y-%m") for row in cur.fetchall()]
        return available_dates
    except Exception as e:
        st.error(f"Error fetching available dates: {e}")
        return []

@st.cache_data(ttl='30d',max_entries=10000,show_spinner=False)
def get_crime_street_level_point_dates(lat, lon, dates, radius_meters=1609.34):
    query = """
    SELECT crime_type, crime_id, month, latitude, longitude
    FROM crimes
    WHERE ST_DWithin(
        geom,
        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
        %s
    )
    AND month BETWEEN %s AND %s;
    """
    
    with st.session_state["db_connection"].cursor() as cur:
        date_start_fmt = f"{dates[0]}-01"
        date_end_fmt = f"{dates[-1]}-01"
        print(lon, lat, radius_meters, date_start_fmt, date_end_fmt)
        cur.execute(query, (lon, lat, radius_meters, date_start_fmt, date_end_fmt))
        data = cur.fetchall()
    return pd.DataFrame(data, columns=['crime_type', 'crime_id', 'month', 'latitude', 'longitude'])

# TODO: Test this function!
@st.cache_data(ttl='30d',max_entries=10000,show_spinner=False)
def get_crime_street_level_area_dates(polygon_points, dates):
    polygon_str = ",".join(f"{lon} {lat}" for lon, lat in polygon_points)
    polygon_wkt = f"POLYGON(({polygon_str}, {polygon_points[0][0]} {polygon_points[0][1]}))"

    query = """
    SELECT crime_type, crime_id, month, latitude, longitude
    FROM crimes
    WHERE ST_Within(
        geom, 
        ST_GeomFromText(%s, 4326)
    )
    AND month BETWEEN %s AND %s;
    """
    
    with st.session_state["db_connection"].cursor() as cur:
        date_start_fmt = f"{dates[0]}-01"
        date_end_fmt = f"{dates[-1]}-01"
        cur.execute(query, (polygon_wkt, date_start_fmt, date_end_fmt))
        data = cur.fetchall()

    return pd.DataFrame(data, columns=['crime_type', 'crime_id', 'month', 'latitude', 'longitude'])