import folium
import streamlit as st

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

def add_crime_counts_to_map(crime_df, feature_group):
    if crime_df.shape[0]>0:
        crime_counts = crime_df.value_counts(subset=['location_latitude', 'location_longitude'], sort=False)
        for (lat, lon), count in crime_counts.items():
            feature_group.add_child(
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
    if status_code==200 and not f_error:
        st.write(address)
    if status_code==503:
        st.write("Crime API error: More than 10,000 crimes in selected region. Retry a different region.")
    elif status_code==400:
        st.write("Crime API error: Too many vertices in selected area. Create a new are with less vertices.")
    elif status_code!=200:
        st.write(f"Crime API error: Unkown error, status_code {status_code}. Retry query.")
    if f_error:
        st.write(f"Postcode error: {error}")