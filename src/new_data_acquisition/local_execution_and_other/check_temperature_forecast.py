from utils_s3 import read_csv_from_s3
import pandas as pd

df_temp = read_csv_from_s3("raw_data/temperature_forecast_data.csv")

print(df_temp.columns)
print(df_temp["Datetime"].min(), "→", df_temp["Datetime"].max())

df_temp["Datetime"] = pd.to_datetime(df_temp["Datetime"])

# Basic check (limited rows) for values for all columns within timeframe
df_zoom = df_temp[
    (df_temp["Datetime"] >= "2025-04-29 00:00:00")
    #& (df_temp["Datetime"] <= "2025-04-08 12:00:00")
    & (df_temp["Région"] == "Occitanie")
]

# print(df_zoom[["Datetime", "Région", "hist_t", "temp_02", "temp_08"]])

# Set max rows
with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(df_zoom[["Datetime", "Région", "hist_t", "temp_02", "temp_08", "temp_14", "temp_20", "temp_20:00:00", "temp_08:00:00", "temp_02:00:00"]])

"""# See NaN values within a specific column and a specific timerange

nan_zoom = df_temp[
    (df_temp["Datetime"] >= "2025-04-07 00:00:00") &
    (df_temp["Datetime"] <= "2025-04-08 03:00:00") &
    (df_temp["Région"] == "Occitanie") &
    (df_temp["temp_02"].isna())
]
print(nan_zoom[["Datetime", "Région", "temp_02"]])"""

"""# Get the datetimes with NaNs

nan_times = df_zoom[df_zoom["temp_02"].isna()]["Datetime"]
print(nan_times.tolist())"""
