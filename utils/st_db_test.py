import streamlit as st
import psycopg2
import os
import pandas as pd

@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        dbname="crime_uk",
        user="postgres",
        password=os.environ.get("DB_PASSWORD"),
        host="172.17.0.2",
        port="5432"
    )

conn = get_db_connection()

@st.cache_data(ttl='30d',max_entries=10000,show_spinner=False)
def get_crimes_near_point(lat, lon, date_start, date_end=None, radius_meters=1609.34):
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
    
    with conn.cursor() as cur:
        date_start_fmt = f"{date_start}-01"
        date_end_fmt = f"{date_end}-01" if date_end else date_start_fmt
        cur.execute(query, (lon, lat, radius_meters, date_start_fmt, date_end_fmt))
        data = cur.fetchall()
    
    return pd.DataFrame(data, columns=['crime_type', 'crime_id', 'month', 'latitude', 'longitude'])

def get_crimes_in_area(polygon_points, date_start, date_end=None):
    polygon_str = ",".join(f"{lon} {lat}" for lat, lon in polygon_points)
    polygon_wkt = f"POLYGON(({polygon_str}, {polygon_points[0][1]} {polygon_points[0][0]}))"

    query = """
    SELECT crime_type, crime_id, month, latitude, longitude
    FROM crimes
    WHERE ST_Within(
        geom, 
        ST_GeomFromText(%s, 4326)
    )
    AND month BETWEEN %s AND COALESCE(%s, %s);
    """
    
    with conn.cursor() as cur:
        cur.execute(query, (polygon_wkt, date_start, date_end, date_start))
        data = cur.fetchall()

    return pd.DataFrame(data, columns=['crime_type', 'crime_id', 'month', 'latitude', 'longitude'])
lat, lon = 51.87241068461067, -1.4668464660644533
date_start = "2022-03"
date_end = "2022-04"

crimes_nearby = get_crimes_near_point(lat, lon, date_start, date_end)
st.write(crimes_nearby)
