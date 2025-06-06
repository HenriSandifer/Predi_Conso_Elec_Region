import pandas as pd
from func_get_cons_data import get_regional_consumption
from dictionaries import region_abbr_dict
import argparse
from pathlib import Path

# Get path to local dataset directory (relative to script)
base_dir = Path(__file__).resolve().parent
data_path = base_dir.parent / "data" / "real_cons_data.csv"

# Step 1: Load existing data
try:
    df_existing = pd.read_csv(data_path)
    print("📂 Loaded existing consumption data from local CSV.")
    df_existing["Datetime"] = pd.to_datetime(df_existing["Datetime"]).dt.tz_localize(None)
except Exception as e:
    print(f"⚠️ Could not load existing data: {e}")
    df_existing = pd.DataFrame(columns=["Datetime", "Consommation (MW)", "Région"])

# Step 2: Determine the last datetime
if not df_existing.empty:
    last_dt = df_existing["Datetime"].max()
else:
    last_dt = pd.to_datetime("2025-01-01")

print(f"🔍 Fetching new data from after: {last_dt}")

# Step 3: Fetch new data
all_new_data = []
for region in region_abbr_dict.keys():
    print(f"📥 Fetching consumption for {region}...")
    df_new = get_regional_consumption(region, last_dt)
    df_new["Datetime"] = pd.to_datetime(df_new["Datetime"]).dt.tz_localize(None)

    if not df_new.empty:
        df_new = df_new[df_new["Datetime"] > last_dt]
        if not df_new.empty:
            all_new_data.append(df_new)

# Step 4: Combine and save locally
if all_new_data:
    df_new_combined = pd.concat(all_new_data).reset_index(drop=True)
    df_updated = pd.concat([df_existing, df_new_combined]).drop_duplicates(subset=["Datetime", "Région"])
    df_updated.sort_values(["Datetime", "Région"], inplace=True)
    print(f"🆕 Appended {len(df_new_combined)} new rows.")
else:
    print("✅ No new data found.")
    df_updated = df_existing

df_updated.to_csv(data_path, index=False)
print(f"✅ Updated CSV saved locally at {data_path}")
