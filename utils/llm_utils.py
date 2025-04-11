import os
import json
import time
import streamlit as st
import pandas as pd
import utils.crime_data_fetch as api
import utils.crime_data_db as db
import utils.data_utils as dutils
from mistralai import Mistral

MODEL = "mistral-large-latest"
# MODEL = "mistral-small-latest"

def _process_df_stats_into_str(crime_df):
    # Group by month and crime_type to get counts
    crime_type_month_counts = (
        crime_df.groupby([pd.Grouper(key='month', freq='ME'), 'crime_type'])
        .size()
        .reset_index(name='Count')
    )
    crime_type_month_counts.columns = ['Month', 'Crime Type', 'Count']

    # Total count for each crime type
    crime_type_total_counts = (
        crime_type_month_counts.groupby('Crime Type')['Count']
        .sum()
        .sort_values()
        .reset_index()
    )

    # Total count for each month
    crime_month_total_counts = (
        crime_type_month_counts.groupby('Month')['Count']
        .sum()
        .sort_index()
        .reset_index()
    )
    total_crimes = crime_type_month_counts['Count'].sum()
    crime_type_month_counts['Month'] = crime_type_month_counts['Month'].dt.strftime('%Y-%m')
    crime_month_total_counts['Month'] = crime_month_total_counts['Month'].dt.strftime('%Y-%m')
    crime_type_month_counts = crime_type_month_counts.to_string(index=False)
    crime_type_total_counts = crime_type_total_counts.to_string(index=False)
    crime_month_total_counts = crime_month_total_counts.to_string(index=False)
    stats = f"Crimes per month per crime type\n{crime_type_month_counts}\n\
        Total crimes per crime type\n{crime_type_month_counts}\n\
        Total crimes per month\n{crime_month_total_counts}\n\
        Total number of crimes: {total_crimes}"
    return stats

def _generate_date_range(start_year, start_month, end_year, end_month):
    """
    Generate a date range between two points in time.
    
    This function creates a lists of dates in YYYY-MM format that contains all
    months from start date to end date (inclusive)
    
    Parameters:
    -----------
    start_year : int
        Starting year for the date range
    start_month : int
        Starting month (1-12) for the date range
    end_year : int
        Ending year for the date range
    end_month : int
        Ending month (1-12) for the date range
        
    Returns:
    --------
    list str
        list of date strings in 'YYYY-MM' format
    """
    # Generate date range
    dates = []
    year, month = start_year, start_month

    while (year, month) <= (end_year, end_month):
        # Format date as YYYY-MM with zero padding
        dates.append(f"{year:04d}-{month:02d}")
        # Move to next month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return dates

def tool_get_crime_street_level_point_dates(lat, lon, start_year, start_month, end_year, end_month):
    """
    Retrieves crime data one mile around a specific location and returns statistics as text.

    Parameters:
    -----------
    lat : str
        Latitude coordinate of the location.
    long : str
        Longitude coordinate of the location.
    start_year : str
        Starting year for the date range
    start_month : str
        Starting month (1-12) for the date range
    end_year : str
        Ending year for the date range
    end_month : str
        Ending month (1-12) for the date range
    
    Returns:
    --------
    str
        A string containing:
        - Count of crimes per type per month. Categories:
            'anti-social-behaviour', 'bicycle-theft', 'burglary',
            'criminal-damage-arson', 'drugs', 'other-theft', 'possession-of-weapons',
            'public-order', 'robbery', 'shoplifting', 'theft-from-the-person',
            'vehicle-crime', 'violent-crime', 'other-crime'
        - Total crimes per crime type
        - Total crimes per month
        - Total crimes in all months
    """
    lat = float(lat)
    lon = float(lon)
    start_year = int(start_year)
    start_month = int(start_month)
    end_year = int(end_year)
    end_month = int(end_month)
    dates = _generate_date_range(start_year, start_month, end_year, end_month)
    if st.session_state["db_connection"] != None:
        df = db.get_crime_street_level_point_dates(lat, lon, dates)
    else:
        df = api.get_crime_street_level_point_dates(lat, lon, dates)
    stats_as_str = _process_df_stats_into_str(df)
    return stats_as_str

def tool_get_crime_street_level_postcode_dates(postcode, start_year, start_month, end_year, end_month):
    """
    Retrieves crime data one mile around a specific postcode and returns statistics as text.

    Parameters:
    -----------
    postcode : str
        Postcode
    start_year : str
        Starting year for the date range
    start_month : str
        Starting month (1-12) for the date range
    end_year : str
        Ending year for the date range
    end_month : str
        Ending month (1-12) for the date range
    
    Returns:
    --------
    str
        A string containing:
        - Count of crimes per type per month. Categories:
            'anti-social-behaviour', 'bicycle-theft', 'burglary',
            'criminal-damage-arson', 'drugs', 'other-theft', 'possession-of-weapons',
            'public-order', 'robbery', 'shoplifting', 'theft-from-the-person',
            'vehicle-crime', 'violent-crime', 'other-crime'
        - Total crimes per month
        - Total crimes in all months
    """
    f_error, error, postcode_info = api.get_postcode_info_from_postcode(postcode)
    if f_error:
        return f"The following error happened while trying to get information about the postcode: {error}"
    else:
        start_year = int(start_year)
        start_month = int(start_month)
        end_year = int(end_year)
        end_month = int(end_month)
        stats_as_str = tool_get_crime_street_level_point_dates(postcode_info["latitude"], postcode_info["longitude"], start_year, start_month, end_year, end_month)
        return stats_as_str

tools = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_crime_street_level_point_dates",
            "description": "Retrieves crime data one mile around a specific \
                location within a date range and returns the number crimes per \
                month per crime type, the number of crimes per month, the number \
                of crimes per crime type and the total number of crimes",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "string",
                        "description": "Latitude of the location",
                    },
                    "lon": {
                        "type": "string",
                        "description": "Longitude of the location.",
                    },
                    "start_year": {
                        "type": "string",
                        "description": "Start year in format YYYY of the range of months.",
                    },
                    "start_month": {
                        "type": "string",
                        "description": "Start month in format MM of the range of months.",
                    },
                    "end_year": {
                        "type": "string",
                        "description": "End year in format YYYY of the range of months.",
                    },
                    "end_month": {
                        "type": "string",
                        "description": "End month in format MM of the range of months.",
                    }
                },
                "required": ["lat", "lon", "start_year", "start_month", "end_year", "end_month"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_crime_street_level_postcode_dates",
            "description": "Retrieves crime data one mile around a specific \
                postcode within a date range and returns the number crimes per \
                month per crime type, the number of crimes per month, the number \
                of crimes per crime type and the total number of crimes",
            "parameters": {
                "type": "object",
                "properties": {
                    "postcode": {
                        "type": "string",
                        "description": "The transaction id.",
                    },
                    "start_year": {
                        "type": "string",
                        "description": "Start year in format YYYY of the range of months.",
                    },
                    "start_month": {
                        "type": "string",
                        "description": "Start month in format MM of the range of months.",
                    },
                    "end_year": {
                        "type": "string",
                        "description": "End year in format YYYY of the range of months.",
                    },
                    "end_month": {
                        "type": "string",
                        "description": "End month in format MM of the range of months.",
                    }
                },
                "required": ["postcode", "start_year", "start_month", "end_year", "end_month"],
            },
        },
    },
]

names_to_functions = {
    'tool_get_crime_street_level_point_dates': tool_get_crime_street_level_point_dates,
    'tool_get_crime_street_level_postcode_dates': tool_get_crime_street_level_postcode_dates
}

@st.dialog("Mistral AI API Key Required")
def get_api_key():
    flag = False
    col1, col2 = st.columns([0.7,0.3], vertical_alignment="bottom")
    with col1:
        api_key = st.text_input("Enter your [Mistral AI](https://console.mistral.ai/) API Key", type="password")
    with col2:
        if st.button("Submit"):
            flag = True
    if flag == True:
        if len(api_key) != 32:
            st.error("Length of the API key is incorrect.")
        else:
            st.session_state.api_key = api_key
            if "api_key" in st.session_state and st.session_state.api_key:
                st.rerun()

def llm_connect():
    if "api_key" in st.session_state and st.session_state.api_key:
        st.session_state["llm_conn"] = Mistral(api_key=st.session_state.api_key)
    else:
        st.session_state["llm_conn"] = None

def llm_query(messages):
    response = st.session_state["llm_conn"].chat.complete(
            model = MODEL,
            messages = messages,
            max_tokens = 1000,
            tools = tools
        )
    print(response)
    if response.choices[0].message.tool_calls != None:
        messages.append(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)
            function_result = names_to_functions[function_name](**function_params)
            messages.append({
                "role":"tool", 
                "name":function_name, 
                "content":function_result, 
                "tool_call_id":tool_call.id,
            })
        response = st.session_state["llm_conn"].chat.complete(
            model = MODEL,
            messages = messages
        )
        return response.choices[0].message.content
    else:
        return response.choices[0].message.content

def chat_stream(response):
    for char in response:
        yield char
        time.sleep(.001)

def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]
