import pandas as pd
from utils_s3 import write_csv_to_s3

# Paths to your local files
real_temp_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\reg_2025_temperature.csv"
pred_temp_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Pipelines\regional_temp_forecast.csv"

# Read CSVs
df_real = pd.read_csv(real_temp_path)
df_pred = pd.read_csv(pred_temp_path)

# Ensure proper datetime and sorting
df_real["Datetime"] = pd.to_datetime(df_real["Datetime"])
df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])

df_pred["Datetime"] = df_pred["Datetime"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)

df_real = df_real.sort_values("Datetime")
df_pred = df_pred.sort_values("Datetime")

# Rename temperature column in both
df_real = df_real.rename(columns={"t": "hist_t"})
df_pred = df_pred.rename(columns={"t": "temp_02"})

# Merge both on Datetime and Region (outer to include all future forecast points)
df_merged = pd.merge(df_real, df_pred, on=["Datetime", "Région"], how="outer")

# Sort and reset index
df_merged = df_merged.sort_values(["Datetime", "Région"]).reset_index(drop=True)

# Upload to S3
archive_key = "raw_data/temperature_forecast_data.csv"
write_csv_to_s3(df_merged, archive_key)

print("✅ Initial versioned temperature archive uploaded to S3")
