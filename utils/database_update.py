import os
import requests
import zipfile
import pandas as pd
import psycopg2
import shutil

# PostgreSQL connection details
# Check DB_HOST with "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgresql-server"
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DATA_URL = "https://data.police.uk/data/archive/latest.zip"
DOWNLOAD_PATH = "../../latest.zip"
EXTRACT_PATH = "../../crime_data"


def getPaths(data_path = '.', ext=".csv"):
    """
    Gets all files that include the string ext within the given path.
    """
    filepaths = []
    for subdir, dirs, files in os.walk(data_path):
        for file in files:
            filepaths.append(os.path.join(subdir, file))
    filepaths.sort()
    return [i for i in filepaths if ext in i]

# Download the latest crime data
def download_crime_data():
    print("Downloading latest crime data...")
    response = requests.get(DATA_URL, stream=True)
    with open(DOWNLOAD_PATH, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
    print("Download complete.")

# Extract ZIP file
def extract_data():
    print("Extracting files...")
    with zipfile.ZipFile(DOWNLOAD_PATH, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)
    print("Extraction complete.")

# Process CSV files and insert into database
def process_and_load_data():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    paths = getPaths(data_path=EXTRACT_PATH, ext="street.csv")
    
    # Default columns in the csv
    required_columns = ['Crime ID','Month','Reported by','Falls within','Longitude',
                        'Latitude','Location','LSOA code','LSOA name','Crime type',
                        'Last outcome category','Context']
    for file_path in paths:
        print(f"Processing {file_path}...")
        df = pd.read_csv(file_path)
        
        # Convert Month to date
        df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m").dt.date
        
        for col in required_columns:
            if col not in df.columns:
                print(f"Warning: Adding empty column {col}")
                df[col] = None

        total_rows = len(df)
        print(f"{total_rows} records to process...")

        for i, (_, row) in enumerate(df.iterrows(), 1):
            # Check if Longitude or Latitude is missing
            if pd.isna(row["Longitude"]) or pd.isna(row["Latitude"]):
                geom_value = None  # Insert NULL for missing coordinates
            else:
                geom_value = f"ST_SetSRID(ST_MakePoint({row['Longitude']}, {row['Latitude']}), 4326)"
            cursor.execute("""
                INSERT INTO crimes (crime_id, month, reported_by, falls_within, longitude, latitude, location, lsoa_code, lsoa_name, crime_type, last_outcome_category, context, geom)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
                ON CONFLICT (crime_id) 
                DO UPDATE SET 
                    month = EXCLUDED.month,
                    reported_by = EXCLUDED.reported_by,
                    falls_within = EXCLUDED.falls_within,
                    longitude = EXCLUDED.longitude,
                    latitude = EXCLUDED.latitude,
                    location = EXCLUDED.location,
                    lsoa_code = EXCLUDED.lsoa_code,
                    lsoa_name = EXCLUDED.lsoa_name,
                    crime_type = EXCLUDED.crime_type,
                    last_outcome_category = EXCLUDED.last_outcome_category,
                    context = EXCLUDED.context,
                    geom = EXCLUDED.geom;
            """, (
                row["Crime ID"], row["Month"], row["Reported by"], row["Falls within"], 
                row["Longitude"], row["Latitude"], row["Location"], row["LSOA code"], 
                row["LSOA name"], row["Crime type"], row["Last outcome category"],
                row["Context"], row["Longitude"], row["Latitude"]
            ))
            
            if i % (total_rows // 10 + 1) == 0:  # Print progress every ~10%
                print(f"{i}/{total_rows} records processed...")
        
        conn.commit()
        print(f"Finished processing {file_path}")

    cursor.close()
    conn.close()
    print("Database updated successfully!")

def remove_downloaded_files():
    print("Removing downloaded files")
    os.remove(DOWNLOAD_PATH)
    shutil.rmtree(EXTRACT_PATH)
    print("Removed files")

# TODO: Use logging instead of printing
if __name__ == "__main__":
    download_crime_data()
    extract_data()
    process_and_load_data()
    remove_downloaded_files()
