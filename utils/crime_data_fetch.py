import requests
import pandas as pd
from datetime import datetime
import streamlit as st

CATEGORIES =[
    'anti-social-behaviour', 'bicycle-theft', 'burglary',
    'criminal-damage-arson', 'drugs', 'other-theft', 'possession-of-weapons',
    'public-order', 'robbery', 'shoplifting', 'theft-from-the-person',
    'vehicle-crime', 'violent-crime', 'other-crime'
]

@st.cache_data(ttl='1d',max_entries=10000,show_spinner=False)
def get_postcode_info_from_postcode(postcode):
    postcode = postcode.replace(" ", "").upper()
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(url)
    response_json = response.json()
    if "error" in response_json:
        error = response_json["error"]
        postcode = "SL41PE"
        url = f"https://api.postcodes.io/postcodes/{postcode}"
        response = requests.get(url)
        response_json = response.json()
        return True, error, response_json["result"]
    else:
        return False, "", response_json["result"]

@st.cache_data(ttl='1d',max_entries=10000,show_spinner=False)
def get_postcode_info_from_lat_long(lat, long):
    lat, long = str(lat), str(long)
    url = f"https://api.postcodes.io/postcodes/"
    params = {
        "lon": long,
        "lat": lat
    }
    response = requests.get(url, params)
    response_json = response.json()
    if "error" in response_json:
        error = response_json["error"]
        postcode = "SL41PE"
        url = f"https://api.postcodes.io/postcodes/{postcode}"
        response_json = response.json()
        return True, error, response_json["result"]
    else:
        return False, "", response_json["result"]

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m")
        return True
    except ValueError:
        return False

def get_crime_categories(date):
    if is_valid_date_format(date):
        url = "https://data.police.uk/api/crime-categories"
        params = {"date": date}
        response = requests.get(url, params)
        return response.json()
    else:
        return []

# Find the neighbourhood policing team responsible for a particular area from
# latitude and longitud. 
def locate_neighbourhood(lat, long):
    base_url = "https://data.police.uk/api/locate-neighbourhood"
    params = {'q': f"{lat},{long}"}
    response = requests.get(base_url, params)
    return response.json()

# Get neighbourhood boundary as a list of latitude/longitude pairs.
def get_boundary_neighbourhood(lat, long):
    neigh = locate_neighbourhood(lat, long)
    url = f"https://data.police.uk/api/{neigh['force']}/{neigh['neighbourhood']}/boundary"
    response = requests.get(url)
    return response.json()

# Return a list of available data sets. 
def get_availability():
    base_url = "https://data.police.uk/api/crimes-street-dates"
    response = requests.get(base_url)
    return response.json()

# Returns the crimes occurred in a one mile radius from a given
# latitude and longitude in the form of a list of dict.
@st.cache_data(ttl='1d',max_entries=1000,show_spinner=False)
def get_crime_street_level_point(lat, long, date=None):
    base_url = "https://data.police.uk/api/crimes-street/all-crime"
    params = {
        'lat': lat,
        'lng': long
    }
    if date != None and is_valid_date_format(date):
        params['date'] = date
    response = requests.get(base_url, params)
    if response.status_code == 200:
        return response.json(), 200
    else:
        return [], response.status_code

# Returns just the crimes which occurred at the nearest location from a given
# latitude and longitude in the form of a list of dict.
@st.cache_data(ttl='1d',max_entries=1000,show_spinner=False)
def get_crime_street_level_location(lat, long, date=None):
    base_url = "https://data.police.uk/api/crimes-at-location"
    params = {
        'lat': lat,
        'lng': long
    }
    if date != None and is_valid_date_format(date):
        params['date'] = date
    response = requests.get(base_url, params)
    if response.status_code == 200:
        return response.json(), 200
    else:
        return [], response.status_code

# Returns just the crimes which occurred within the shape created by a list of
# latitude and longitude pairs in the form of a list of dict.
@st.cache_data(ttl='1d',max_entries=1000,show_spinner=False)
def get_crime_street_level_area(list_lat_long, date=None):
    base_url = "https://data.police.uk/api/crimes-street/all-crime"
    list_lat_long_str = [str(lat)+","+str(lon) for lon, lat in list_lat_long]
    lat_long = ':'.join(list_lat_long_str)
    params = {
        'poly': lat_long
    }
    if date != None and is_valid_date_format(date):
        params['date'] = date
    response = requests.get(base_url, params)
    if response.status_code == 200:
        return response.json(), 200
    else:
        return [], response.status_code

def list_crimes_to_df(list_crimes):
    return pd.json_normalize(list_crimes, sep='_')

def list_crimes_to_list_coordinates(list_crimes):
    list_coordinates = [
        (crime['location']['latitude'], 
        crime['location']['longitude'])
        for crime in list_crimes
    ]
    return list_coordinates

if __name__ == "__main__":
    postcode = "B5 7TS"
    correct_pc, error, result = get_postcode_info_from_postcode(postcode)
    lat, lon = result["latitude"], result["longitude"]
    data, status_code = get_crime_street_level_point(lat, lon, "2024-01")
    boundary = get_boundary_neighbourhood(lat, lon)
    coordinates = list_crimes_to_list_coordinates(data)
    df = list_crimes_to_df(data)
    print(df['category'].unique())

    print(len(boundary))
    print(len(coordinates))

    print(df.columns)
    print(df.head())

    print(df["category"].value_counts())
    print(df[df["category"]=="violent-crime"].head(20))