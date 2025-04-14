import pandas as pd
from utils_s3 import write_csv_to_s3

# Paths to your local files
real_cons_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\reg_2025_cons.csv"

# Read CSVs
df_cons = pd.read_csv(real_cons_path)

# Ensure proper datetime and sorting
df_cons["Datetime"] = pd.to_datetime(df_cons["Datetime"], utc=True).copy()

df_cons["Datetime"] = df_cons["Datetime"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)

df_cons = df_cons.sort_values(["Datetime", "Région"]).reset_index(drop=True)

# Upload to S3
archive_key = "raw_data/real_cons_data.csv"
write_csv_to_s3(df_cons, archive_key)

print("✅ Initial consumption archive uploaded to S3")
