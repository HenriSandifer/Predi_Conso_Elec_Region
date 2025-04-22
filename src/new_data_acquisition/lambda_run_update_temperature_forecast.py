import pandas as pd
import argparse
from dictionaries import region_abbr_dict
from func_get_temperature_forecast import regional_temperature_prediction
from utils_s3 import read_csv_from_s3, write_csv_to_s3


def lambda_handler(event, context):

    def run_temperature_forecast_update(run_time_str):
        # Define target day (D0) and overwrite line (D+1 @ 00:00)
        today = pd.to_datetime("today").normalize()
        target_day = today
        ow_line = (target_day + pd.Timedelta(days=1)).normalize()

        print(f"🕒 Running forecast update for run_time = {run_time_str} (D+1 starts at {ow_line})")

        # Step 1: Fetch new forecasts
        all_new_temp_data = []
        for region in region_abbr_dict.keys():
            print(f"🔄 Fetching forecast for {region} on {target_day.strftime('%Y-%m-%d')}...")
            df_region = regional_temperature_prediction(region)
            if not df_region.empty:
                all_new_temp_data.append(df_region)

        df_new_forecast = pd.concat(all_new_temp_data).reset_index(drop=True)
        df_new_forecast["Datetime"] = pd.to_datetime(df_new_forecast["Datetime"])

        # Step 2: Load existing archive from S3
        archive_key = "raw_data/temperature_forecast_data.csv"
        df_existing = read_csv_from_s3(archive_key)

        if df_existing is None:
            print("⚠️ No existing archive found. Creating new versioned archive.")
            df_existing = df_new_forecast[["Datetime", "Région"]].copy()

        df_existing["Datetime"] = pd.to_datetime(df_existing["Datetime"])

        # Step 3: Merge new data into column like temp_02, temp_08, etc.
        run_time_column = f"temp_{run_time_str}"

        df_new_forecast["Datetime"] = df_new_forecast["Datetime"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)
        df_new_subset = df_new_forecast[["Datetime", "Région", "t"]].copy()
        df_new_subset = df_new_subset[df_new_subset["Datetime"] >= ow_line]

        # Set indexes for clean join
        df_existing.set_index(["Datetime", "Région"], inplace=True)
        df_new_subset.set_index(["Datetime", "Région"], inplace=True)

        # Reset index to safely merge
        df_existing = df_existing.reset_index()

        # Merge new timestamps/regions if they don't exist yet
        df_missing_rows = df_new_subset.reset_index()[["Datetime", "Région"]].drop_duplicates()

        df_existing = pd.merge(
            df_existing,
            df_missing_rows,
            on=["Datetime", "Région"],
            how="outer"
        ).sort_values(["Datetime", "Région"]).reset_index(drop=True)

        df_existing.set_index(["Datetime", "Région"], inplace=True)

        # Inject updated forecast into correct column
        df_existing.loc[df_new_subset.index, run_time_column] = df_new_subset["t"]

        # Reset index and save back to S3
        df_existing.reset_index(inplace=True)
        write_csv_to_s3(df_existing, archive_key)

        print("✅ Temperature forecast archive updated successfully.")