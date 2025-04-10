from utils.dictionaries import weather_coordinates, region_abbr_caps_dict
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

    # Resample to 15-minute intervals and interpolate
    df_avg.set_index("Datetime", inplace=True)
    wdata_resampled = (
        df_avg.groupby("Région", group_keys=False)
        .resample("15min")
        .interpolate(method="linear")
    )
    wdata_resampled.reset_index(inplace=True)
    wdata_resampled["Région"] = wdata_resampled["Région"].ffill()

    return wdata_resampled



