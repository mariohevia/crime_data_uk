import folium
import streamlit as st
import utils.crime_data_fetch as api
import math

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

# TODO: Should this function be moved to a utils.py file?
def _normalise(value, max_count, scale=60):
    return (value / max_count) * scale if max_count > scale else value

def add_crime_counts_to_map(crime_df, feature_group):
    """
    Adds crime data as interactive circles to a Folium map.
    
    This function processes a DataFrame of crime data, counts occurrences at each
    location, and adds circles to the map with size and color proportional to 
    crime frequency. Each circle includes a tooltip showing total crimes and
    breakdown by category.
    
    Parameters:
    -----------
    crime_df : pandas.DataFrame
        DataFrame containing crime data with 'location_latitude', 'location_longitude',
        and 'category' columns.
    feature_group : folium.FeatureGroup
        The Folium feature group to add the crime bubbles to.
    
    Returns:
    --------
    None
        The function modifies the feature_group in place.
    """
    # Only proceed if the DataFrame contains data
    if crime_df.shape[0]>0:
        # Count total crimes at each unique location
        crime_counts = crime_df.value_counts(subset=['latitude', 'longitude'], sort=False)
        max_counts = crime_counts.max()

        # Count crimes per category at each location
        category_counts = crime_df.groupby(['latitude', 'longitude', 'crime_type']).size()

        # Iterate through each location and its crime count
        for (lat, lon), total_count in crime_counts.items():
            # Normalize the count for visual scaling
            norm_total_count = _normalise(total_count, max_counts)

            # Get crime counts for different categories at this location
            category_data = category_counts.loc[lat, lon] if (lat, lon) in category_counts.index else {}
            
            # Format the category breakdown for tooltip display
            category_tooltip = "<br>".join([f"{cat}: {count}" for cat, count in category_data.items()])

            # Create tooltip text
            tooltip_text = f"Total crimes: {total_count}<br>{category_tooltip}"

            # Add circle marker to the map
            feature_group.add_child(
                folium.Circle(
                    location=[lat, lon],
                    radius=10 + norm_total_count * 2,  # Scale size based on occurrences
                    color=color_function(norm_total_count), # Color based on crime intensity
                    # stroke=False,
                    fill=True,
                    fill_color=color_function(norm_total_count),
                    fill_opacity=0.6,
                    tooltip=tooltip_text # Interactive tooltip with crime details
                ))

pfa_no_data=["Greater Manchester"]
country_lower_levels=["Scotland"]

def write_selected_location_in_st(f_error, error, postcode_info, lat, lon, status_code):
    if type(postcode_info) == list:
        postcode_info = postcode_info[0]
    st.subheader("Selected location")
    if postcode_info != None and not f_error:
        address = f"{postcode_info['postcode']}, \
            {postcode_info['admin_ward']}, \
            {postcode_info['admin_district']}\
            \n{postcode_info['region']}, \
            {postcode_info['country']}\
            \nLatitude: {lat:.6f}, Longitude: {lon:.6f}"
    else:
        address = f"Latitude: {lat:.6f}, Longitude: {lon:.6f}"
    if postcode_info != None and not f_error:
        if postcode_info['pfa'] in pfa_no_data:
            st.write(f":red[{postcode_info['pfa']} does not provide complete crime data. Crime levels may appear much lower than they really are.]" )
        if postcode_info['country'] in country_lower_levels:
            st.write(f":red[{postcode_info['country']} does not provide complete crime data. Crime levels may appear much lower than they really are.]" )
    if status_code==200 and not f_error:
        st.write(address)
    if status_code==503:
        st.write("Crime API error: More than 10,000 crimes in selected region. Retry a different region.")
    elif status_code==400:
        st.write("Crime API error: Too many vertices in selected area. Create a new area with less vertices.")
    elif status_code!=200:
        st.write(f"Crime API error: Unkown error, status_code {status_code}. Retry query.")
    if f_error:
        st.write(f"Postcode error: {error}")