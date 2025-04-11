from utils.dictionaries import region_abbr_dict
from api.get_temperature_forecast import regional_temperature_prediction
import pandas as pd

# For example, target today's date or yesterday
target_day = pd.to_datetime("today").normalize() - pd.Timedelta(days=1)

# Store all regional predictions
all_new_temp_data = []

for region in region_abbr_dict.keys():
    print(f"🔄 Fetching forecast for {region} on {target_day.strftime('%Y-%m-%d')}...")
    df_region = regional_temperature_prediction(region, target_day)
    if not df_region.empty:
        all_new_temp_data.append(df_region)

# Combine all into one big dataframe
df_national_temp_forecast = pd.concat(all_new_temp_data).reset_index(drop=True)

"""Use code from get_consumption_data.py script for proper concatenation
protocol into monthly dataset"""

# Optional: Save to CSV
df_national_temp_forecast.to_csv("regional_temp_forecast.csv", index=False)
