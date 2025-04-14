from utils_s3 import read_csv_from_s3
import pandas as pd

df_temp = read_csv_from_s3("raw_data/temperature_forecast_data.csv")

print(df_temp.columns)
print(df_temp["Datetime"].min(), "→", df_temp["Datetime"].max())

df_temp["Datetime"] = pd.to_datetime(df_temp["Datetime"])

df_zoom = df_temp[
    (df_temp["Datetime"] >= "2025-04-15 00:00:00") &
    (df_temp["Datetime"] <= "2025-04-15 02:00:00") &
    (df_temp["Région"] == "Auvergne-Rhône-Alpes")
]
print(df_zoom[["Datetime", "Région", "hist_t", "temp_02", "temp_08"]])
