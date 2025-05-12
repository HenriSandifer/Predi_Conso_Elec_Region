import requests
import pandas as pd

# Base URL for the API.
# (In the documentation, the sample uses http://127.0.0.1:8000.
# In your production or test environment, update this base URL accordingly.)
BASE_URL = "https://meteo.comptoir.net/api/synops"

def fetch_station_measures(station_id, target_date, fields="measured_at,t"):
    """
    For a given station ID and target_date (string in YYYY-MM-DD format),
    fetch measures for that date using the API.
    
    Returns a DataFrame with columns 'measured_at' and 't' (temperature).
    """
    # Construct the URL:
    # E.g.: https://meteo.comptoir.net//89642/2025-02-20?fields=measured_at,t
    url = f"{BASE_URL}/{station_id}/{target_date}?fields={fields}"
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching station {station_id} for {target_date}: HTTP {response.status_code}")
        return None

    data = response.json()
    
    # Check the JSON structure. Depending on the API, the measures may be nested.
    # Here we assume that the JSON has a top-level key "measures" which is a list of dictionaries,
    # each containing the fields "measured_at" and "t".
    if "measures" not in data:
        print(f"Unexpected data format for station {station_id}: {data}")
        return None

    # Create a DataFrame from the "measures" list.
    df = pd.DataFrame(data["measures"])
    
    # Sometimes the API may nest fields inside another key; adjust accordingly if needed.
    # For example, if the actual fields are inside a sub-dictionary (e.g., "record" or "fields"),
    # you would extract them. For now, we'll assume they are at the top level.
    
    # Convert measured_at to datetime.
    if "measured_at" in df.columns:
        df["measured_at"] = pd.to_datetime(df["measured_at"])
    else:
        print(f"'measured_at' not found in data for station {station_id}.")
        return None
    
    # Ensure temperature is numeric.
    if "t" in df.columns:
        df["t"] = pd.to_numeric(df["t"], errors="coerce")
    else:
        print(f"'t' not found in data for station {station_id}.")
        return None
    
    # Return the DataFrame with the two columns.
    return df[["measured_at", "t"]].copy()




