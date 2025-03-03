import requests
import pandas as pd
from datetime import datetime

def get_lat_long_from_postcode(postcode):
    postcode = postcode.replace(" ", "").upper()
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(url)
    response_json = response.json()
    if "error" in response_json:
        print(response_json["error"])
        return 0, 0
    else:
        return (response_json["result"]["latitude"], 
                response_json["result"]["longitude"])

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

def locate_neighbourhood(lat, long):
    base_url = "https://data.police.uk/api/locate-neighbourhood"
    params = {'q': f"{latitude},{longitude}"}
    response = requests.get(base_url, params)
    return response.json()

def get_availability():
    base_url = "https://data.police.uk/api/crimes-street-dates"
    response = requests.get(base_url)
    return response.json()

def get_crime_street_level_point(lat, long, date=None):
    base_url = "https://data.police.uk/api/crimes-street/all-crime"
    params = {
        'lat': lat,
        'lng': long
    }
    if date != None and is_valid_date_format(date):
        params['date'] = date
    response = requests.get(base_url, params)
    return response.json()

def get_crime_street_level_postcode(postcode, date=None):
    lat, long = get_lat_long_from_postcode(postcode)
    return get_crime_street_level_point(lat, long, date)

def list_crimes_to_df(list_crimes):
    return pd.json_normalize(data, sep='_')

if __name__ == "__main__":
    data = get_crime_street_level_postcode("B5 7TS", "2024-01")
    df = list_crimes_to_df(data)

    print(df.columns)
    print(df.head())

    print(df["category"].value_counts())
    print(df[df["category"]=="violent-crime"].head(20))