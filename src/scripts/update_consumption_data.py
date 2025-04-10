from utils.dictionaries import region_abbr_dict
from api.get_consumption_data import get_regional_consumption
import pandas as pd

# For example, target today's date or yesterday
target_day = pd.to_datetime("today").normalize() - pd.Timedelta(days=1)

# Gather new data
all_new_cons_data = []

for region in region_abbr_dict.keys():
    print(f"📥 Fetching data for {region} on {target_day.strftime('%Y-%m-%d')}...")
    df_region = get_regional_consumption(region, target_day)
    if not df_region.empty:
        all_new_cons_data.append(df_region)

# Combine new data
df_new = pd.concat(all_new_cons_data).reset_index(drop=True)

# Save without concatenating
output_path = f"data/tests/consumption_data_{target_day.strftime('%Y-%m-%d')}.csv"
df_new.to_csv(output_path, index=False)
print("✅ Finished saving regional consumption data.")

