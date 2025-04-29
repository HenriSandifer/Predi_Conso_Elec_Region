import pandas as pd
from func_get_cons_data import get_regional_consumption
from utils_s3 import read_csv_from_s3, write_csv_to_s3
from dictionaries import region_abbr_dict

# Set AWS S3 path
S3_FILENAME = "raw_data/real_cons_data.csv"

# Step 1: Load existing data
try:
    df_existing = read_csv_from_s3(S3_FILENAME)
    print("📂 Loaded existing consumption data from S3.")
except Exception as e:
    print(f"⚠️ Could not load existing data: {e}")
    df_existing = pd.DataFrame(columns=["Datetime", "Consommation (MW)", "Région"])

# Step 2: Determine the last datetime in the dataset
if not df_existing.empty:
    last_dt = df_existing["Datetime"].max()
else:
    last_dt = pd.to_datetime("2025-01-01")  # Fallback start date

print(f"🔍 Fetching new data from after: {last_dt}")

# Step 3: Get today's date as target_day
target_day = pd.to_datetime("today").normalize()

# Step 4: Fetch new data from API
all_new_data = []
for region in region_abbr_dict.keys():
    print(f"📥 Fetching consumption for {region}...")
    df_new = get_regional_consumption(region, last_dt)
        
    if not df_new.empty:
        df_new = df_new[df_new["Datetime"] > last_dt]
        if not df_new.empty:
            all_new_data.append(df_new)

# Step 5: Combine and append
if all_new_data:
    df_new_combined = pd.concat(all_new_data).reset_index(drop=True)
    df_updated = pd.concat([df_existing, df_new_combined]).drop_duplicates(subset=["Datetime", "Région"])
    df_updated.sort_values(["Datetime", "Région"], inplace=True)
    print(f"🆕 Appended {len(df_new_combined)} new rows.")
else:
    print("✅ No new data found.")
    df_updated = df_existing

# Step 6: Upload back to S3
write_csv_to_s3(df_updated, S3_FILENAME)
print("✅ Updated consumption data saved to S3.")
