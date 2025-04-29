import requests
import pandas as pd
from utils_cons_API_inputs import get_cons_API_inputs

"""Make sure only the relevant timerange is pulled
A matter of hours now, not days
To be modified in prepare_pipeline function"""

def get_regional_consumption(region_name, last_dt):

    # Pull from 1 hour after last known datetime to now (API probably updates hourly)
    end_dt = pd.Timestamp("now").normalize() + pd.Timedelta(hours=23, minutes=59)
    start_dt = last_dt + pd.Timedelta(minutes=15)

    inputs = get_cons_API_inputs(region_name, start_dt, end_dt)
    
    url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records"
    params = {
        "limit": 100,  # increased limit
        "where": inputs["consumption_where"],
        "select": "date,heure,date_heure,libelle_region,consommation",
        "timezone": "UTC",
        "include_links": "false",
        "include_app_metas": "false"
    }
    headers = {"accept": "application/json; charset=utf-8"}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"❌ Error {response.status_code} for region {region_name}")
        return pd.DataFrame()  # return empty df

    consumption_json = response.json()
    df = pd.DataFrame(consumption_json["results"])

    if df.empty:
        print(f"⚠️ No data found for region {region_name}")
        return df

    df["Datetime"] = pd.to_datetime(df["date_heure"], utc=True)\
                                     .dt.tz_convert("Europe/Paris")\
                                     .dt.tz_localize(None)
    
    df = df[["Datetime", "consommation", "libelle_region"]].copy()
    df.rename(columns={"libelle_region": "Région", "consommation": "Consommation (MW)"}, inplace=True)

    df.sort_values("Datetime", inplace=True)

    now_paris = pd.Timestamp("now", tz="Europe/Paris")
    df = df[df["Datetime"] <= now_paris]

    df = df[~df.duplicated(subset=["Datetime"], keep='first')]
    
    # Resample to 15-minute intervals and interpolate
    df.set_index("Datetime", inplace=True)
    cdata_resampled = (
        df.groupby("Région", group_keys=False)
        .resample("15min")
        .mean()
        .infer_objects(copy=False)
    )

    # Interpolate only numeric columns
    numeric_cols = cdata_resampled.select_dtypes(include="number").columns
    cdata_resampled[numeric_cols] = cdata_resampled[numeric_cols].interpolate(method="linear")

    # Forward fill regions
    cdata_resampled.reset_index(inplace=True)
    cdata_resampled["Région"] = cdata_resampled["Région"].ffill()

    return df




