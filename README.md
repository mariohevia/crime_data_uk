# UK Crime Maps
A free and open-source project designed to visualise and analyse geospatial crime data from across the UK.

This project uses interactive crime maps to present publicly available data on crime and policing in England, Wales, and Northern Ireland. Additionally, it provides valuable insights through intuitive visualisations and analyses.

## To dos

+ Check taipy as an alternative option to streamlit.

+ Add postcode or something similar to selected location.

+ Add option to show more months, not just the last one.

+ Show the radius for crimes in map_click.

+ Add a way to show crimes per location and not a radius around the click in map_click.
    + Show the location boundary.

+ Show some statistics below the map of the crimes shown.

+ Mention that for locations in Scotland, only the British Transport Police provide data for Scotland, therefore, crime levels may appear much lower than they really are. 

+ Handle errors (more than 10,000 crimes) for get_crime_street_level_area, get_crime_street_level_location, get_crime_street_level_point.
    + The API will return a 400 status code in response to a GET request longer than 4094 characters. For submitting particularly complex poly parameters, consider using POST instead. 

+ Get only the useful information from maps (https://folium.streamlit.app/limit_data_return) to avoid unnecessary updates when clicking etc.
