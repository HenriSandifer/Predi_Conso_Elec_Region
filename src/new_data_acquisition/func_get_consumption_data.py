import requests
import pandas as pd
from src.new_data_acquisition.utils_cons_API_inputs import get_cons_API_inputs

"""Make sure only the relevant timerange is pulled
A matter of hours now, not days
To be modified in prepare_pipeline function"""

def get_regional_consumption(region_name, target_day):

    # Fake values for model and run_time since they're not needed here
    model = "M36"
    run_time = "02:00:00"

    inputs = get_cons_API_inputs(region_name, target_day.strftime("%Y-%m-%d"), model, run_time)
    
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

    df["Datetime"] = pd.to_datetime(df["date_heure"])
    df = df[["Datetime", "consommation", "libelle_region"]].copy()
    df.rename(columns={"libelle_region": "Région", "consommation": "Consommation (MW)"}, inplace=True)

    df.sort_values("Datetime", inplace=True)
    df["Datetime"] = df["Datetime"].dt.tz_convert("Europe/Paris")
    df.set_index("Datetime", inplace=True)
    df = df.resample("15min").interpolate(method="linear")
    df.reset_index(inplace=True)
    df["Région"] = df["Région"].ffill()

    return df




