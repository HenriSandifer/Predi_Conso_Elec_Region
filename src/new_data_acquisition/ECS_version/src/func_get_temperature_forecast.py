from src.dictionaries import weather_coordinates
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup API client
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def regional_temperature_prediction(region_name):
    """Fetches and processes the temperature forecast for a given French region"""
    cities = weather_coordinates[region_name]
    all_forecasts = []

    for location in cities:
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "hourly": "temperature_2m",
            "models": "meteofrance_seamless"
        }
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "city": location["city"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "Datetime": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_temperature_2m
        }

        df_city = pd.DataFrame(hourly_data)
        all_forecasts.append(df_city)

    # === Processing ===
    df_region_forecast = pd.concat(all_forecasts).reset_index(drop=True)
    df_region_forecast = df_region_forecast.rename(columns={"temperature_2m": "t"})

    # Average temperature across cities
    df_avg = df_region_forecast.groupby("Datetime")["t"].mean().reset_index()
    df_avg["Région"] = region_name

    # Ensure Datetime is parsed correctly and sorted
    df_avg["Datetime"] = pd.to_datetime(df_avg["Datetime"]).dt.tz_convert("Europe/Paris").dt.tz_localize(None)
    df_avg.sort_values(["Région", "Datetime"], inplace=True)

    # Set index before resampling
    df_avg.set_index("Datetime", inplace=True)

    # List to hold each region’s resampled data
    resampled_list = []

    # Process each region individually
    for region, group in df_avg.groupby("Région"):
        # Ensure no duplicate datetime values
        group = group[~group.index.duplicated(keep='first')]

        # Create full datetime range for the region
        full_index = pd.date_range(
            start=group.index.min(), 
            end=group.index.max(), 
            freq="15min"
        )

        # Reindex to enforce presence of every 15-min timestamp
        group_resampled = group.reindex(full_index)

        # Interpolate numeric columns
        numeric_cols = group.select_dtypes(include="number").columns
        group_resampled[numeric_cols] = group_resampled[numeric_cols].interpolate(method="linear")

        # Forward-fill the region name
        group_resampled["Région"] = region

        # Append to list
        resampled_list.append(group_resampled)

    # Combine all resampled data
    df_final = pd.concat(resampled_list).reset_index().rename(columns={"index": "Datetime"})


    return df_final


