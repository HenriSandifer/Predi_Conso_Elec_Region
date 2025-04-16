from utils_s3 import read_csv_from_s3
import pandas as pd

df_cons = read_csv_from_s3("raw_data/real_cons_data.csv")

print(df_cons.columns)
print(df_cons["Datetime"].min(), "→", df_cons["Datetime"].max())

df_cons["Datetime"] = pd.to_datetime(df_cons["Datetime"])

# Basic check (limited rows) for values for all columns within timeframe
df_zoom = df_cons[
    (df_cons["Datetime"] >= "2025-04-09 11:45:00") &
    (df_cons["Datetime"] <= "2025-04-09 23:45:00") &
    (df_cons["Région"] == "Nouvelle-Aquitaine")
]

# print(df_zoom[["Datetime", "Région", "hist_t", "cons_02", "cons_08"]])

# Set max rows
with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(df_zoom[["Datetime", "Région", "Consommation (MW)"]])

"""# See NaN values within a specific column and a specific timerange

nan_zoom = df_cons[
    (df_cons["Datetime"] >= "2025-04-07 00:00:00") &
    (df_cons["Datetime"] <= "2025-04-08 03:00:00") &
    (df_cons["Région"] == "Occitanie") &
    (df_cons["cons_02"].isna())
]
print(nan_zoom[["Datetime", "Région", "cons_02"]])"""

"""# Get the datetimes with NaNs

nan_times = df_zoom[df_zoom["cons_02"].isna()]["Datetime"]
print(nan_times.tolist())"""
