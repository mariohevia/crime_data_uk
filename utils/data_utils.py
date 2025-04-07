import pandas as pd
import utils.crime_data_fetch as api
import utils.crime_data_db as db
import streamlit as st
from datetime import datetime, timedelta

def add_pills_filter_df(df=pd.DataFrame()):
    """
    Creates a category filter using Streamlit pills component and filters the DataFrame accordingly.
    
    This function displays a multi-selection pills component for crime categories and
    filters the input DataFrame based on the user's selection.
    
    Parameters:
    -----------
    df : pandas.DataFrame, optional
        DataFrame containing crime data with a 'category' column.
        Default is an empty DataFrame.
    
    Returns:
    --------
    pandas.DataFrame
        A filtered copy of the input DataFrame containing only the selected categories.
        If the input DataFrame is empty, returns a copy of the original empty DataFrame.
    """
    # Create a pills selector with pretty category names as options
    selection = st.pills("Crime Category", api.FROM_PRETTY_CATEGORIES.keys(), selection_mode="multi", default=api.FROM_PRETTY_CATEGORIES.keys())

    # Only filter if the DataFrame is not empty
    if df.shape[0] != 0:
        # Filter the DataFrame to include only selected categories
        filtered_df = df[df['crime_type'].isin(selection)].copy()
        print(filtered_df.head())
        return filtered_df
    else:
        # Return a copy of the original DataFrame if it's empty
        return df.copy()

def _generate_date_range(start_year, start_month, end_year, end_month):
    # Gnerate date range
    dates = []
    year, month = start_year, start_month

    while (year, month) <= (end_year, end_month):
        dates.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    
    # Create the extended dates list with at least 12 months
    extended_dates = dates.copy()
    
    # If dates list already has 12 or more months, return it as is
    if len(dates) >= 12:
        return dates, extended_dates
    
    # Otherwise, extend the list backward to include at least 12 months
    year, month = start_year, start_month
    
    while len(extended_dates) < 12:
        # Move one month back
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        
        # Add the date at the beginning of the list
        extended_dates.insert(0, f"{year:04d}-{month:02d}")
    
    return dates, extended_dates

def add_start_end_month(key=""):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_map = {i+1: name for i, name in enumerate(month_names)}
    reverse_month_map = {name: i+1 for i, name in enumerate(month_names)}
    
    # Get valid dates if not already in session state
    if key+"valid_dates" not in st.session_state:
        if st.session_state["db_connection"] != None:
            valid_dates = sorted(db.get_availability())
        else:
            valid_dates = sorted([i['date'] for i in api.get_availability()])
        if valid_dates == []:
            current_date = datetime.today()
            month = (current_date.month - 3) % 12 or 12  # Handle month underflow
            year = current_date.year - (1 if current_date.month <= 3 else 0)
            # Format as "YYYY-MM"
            valid_dates = [f"{year:04d}-{month:02d}"]

        valid_years = sorted(set(int(date.split("-")[0]) for date in valid_dates), reverse=True)
        valid_months = {y:[month_map[int(date.split("-")[1])] for date in valid_dates if int(date.split("-")[0]) == y] for y in valid_years}
        st.session_state[key+"valid_dates"] = {
            "valid_years":valid_years,
            "valid_months":valid_months,
            }
    
    # Set default start and end dates if not already in session state
    if key+"start_date" not in st.session_state:
        valid_months = st.session_state[key+"valid_dates"]["valid_months"]
        valid_years = st.session_state[key+"valid_dates"]["valid_years"]
        st.session_state[key+"start_date"] = {
            "start_month":valid_months[valid_years[0]][-1],
            "start_year":valid_years[0],
            }
    if key+"end_date" not in st.session_state:
        valid_months = st.session_state[key+"valid_dates"]["valid_months"]
        valid_years = st.session_state[key+"valid_dates"]["valid_years"]
        st.session_state[key+"end_date"] = {
            "end_month":valid_months[valid_years[0]][-1],
            "end_year":valid_years[0],
            }

    # Update functions used to avoid bug where changing one selectbox twice in a
    # row would not work the second time.
    def update_start_year():
        st.session_state[key+"start_date"]["start_year"] = st.session_state[key+"start_year"]
    def update_start_month():
        st.session_state[key+"start_date"]["start_month"] = st.session_state[key+"start_month"]
    def update_end_year():
        st.session_state[key+"end_date"]["end_year"] = st.session_state[key+"end_year"]
    def update_end_month():
        st.session_state[key+"end_date"]["end_month"] = st.session_state[key+"end_month"]

    col1, col2, _, _, col3, col4 = st.columns(6)
    # Month selection
    years=st.session_state[key+"valid_dates"]["valid_years"]
    with col2:
        if st.session_state[key+"start_date"]["start_year"] in years:
            idx_start_year = years.index(st.session_state[key+"start_date"]["start_year"])
        else:
            idx_start_year = 0
        start_year = st.selectbox("Start Year", years, index=idx_start_year, key=key+"start_year", on_change=update_start_year)
    start_months=st.session_state[key+"valid_dates"]["valid_months"][start_year]
    with col1:
        if st.session_state[key+"start_date"]["start_month"] in start_months:
            idx_start_month = start_months.index(st.session_state[key+"start_date"]["start_month"])
        else:
            idx_start_month = 0
        start_month = st.selectbox("Start Month", start_months, index=idx_start_month, key=key+"start_month", on_change=update_start_month)
    with col4:
        end_years = [y for y in years if y>=start_year]
        if st.session_state[key+"end_date"]["end_year"] in end_years:
            idx_end_year = end_years.index(st.session_state[key+"end_date"]["end_year"])
        else:
            idx_end_year = 0
        end_year = st.selectbox("End Year", end_years, index=idx_end_year, key=key+"end_year", on_change=update_end_year)
    if end_year!=start_year:
        end_months=st.session_state[key+"valid_dates"]["valid_months"][end_year]
    else:
        end_months=st.session_state[key+"valid_dates"]["valid_months"][end_year]
        idx_start_month=end_months.index(start_month)
        end_months=end_months[idx_start_month:]
    with col3:
        if st.session_state[key+"end_date"]["end_month"] in end_months:
            idx_end_month = end_months.index(st.session_state[key+"end_date"]["end_month"])
        else:
            idx_end_month = 0
        end_month = st.selectbox("End Month", end_months, index=idx_end_month, key=key+"end_month", on_change=update_end_month)

    start_month = reverse_month_map[start_month]
    end_month = reverse_month_map[end_month]
    st.session_state[key+"list_crime_dates"],st.session_state[key+"stat_crime_dates"]=_generate_date_range(start_year, start_month, end_year, end_month)

def add_area_plot_crime_statistics(df):
    # 1. Group by month and crime_type to get counts
    crime_counts = df.groupby([pd.Grouper(key='month', freq='M'), 'crime_type']).size().unstack(fill_value=0)

    # 2. Reset index to make month a column
    crime_counts = crime_counts.reset_index()

    # 3. Set the month column as the index (required for Streamlit's area_chart)
    crime_counts = crime_counts.set_index('month')

    # 4. Display the area chart
    st.title('Crime Counts by Type Over Time')
    st.area_chart(crime_counts)

def add_bar_plot_crime_statistics(df):
    # Get total count for each crime type
    crime_type_counts = df['crime_type'].value_counts().reset_index()
    crime_type_counts.columns = ['crime_type', 'count']

    # Sort by count (optional)
    crime_type_counts = crime_type_counts.sort_values('count')

    # Set crime_type as index for Streamlit's bar_chart
    crime_type_counts = crime_type_counts.set_index('crime_type')

    # Create bar chart
    st.title('Total Crimes by Type')
    st.bar_chart(crime_type_counts)