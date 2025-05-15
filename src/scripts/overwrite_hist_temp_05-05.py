import os
import pandas as pd
from datetime import datetime

# Step 2: Overwrite hist_t in forecast file based on datetime + region match
def overwrite_hist_column(forecast_path, hist_df, date_min, date_max):
    df_forecast = pd.read_csv(forecast_path)
    df_forecast["Datetime"] = pd.to_datetime(df_forecast["Datetime"])
    hist_df["Datetime"] = pd.to_datetime(hist_df["Datetime"])

    # Filter for the desired window
    hist_range = hist_df[(hist_df["Datetime"] >= date_min) & (hist_df["Datetime"] <= date_max)]

    # Merge on both Datetime and Région
    df_forecast = df_forecast.merge(
        hist_range[["Datetime", "Région", "t"]],
        on=["Datetime", "Région"],
        how="left",
        suffixes=("", "_new")
    )

    # Overwrite hist_t only for the time range
    date_mask = (df_forecast["Datetime"] >= date_min) & (df_forecast["Datetime"] <= date_max)
    df_forecast.loc[date_mask, "hist_t"] = df_forecast.loc[date_mask, "t"]
    df_forecast.drop(columns=["t"], inplace=True)

    # Save it back
    df_forecast.to_csv(forecast_path, index=False)
    print(f"✅ Forecast file updated with per-region historical temps between {date_min.date()} and {date_max.date()}")

if __name__ == "__main__":
    hist_folder = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Pipelines"
    merged_hist_path = os.path.join(hist_folder, "national_hist_t_05-05.csv")
    forecast_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\s3_downloaded_datasets\temperature_forecast_data.csv"

    date_min = datetime(2025, 4, 5, 0, 0)
    date_max = datetime(2025, 5, 5, 23, 45)

    hist_df = pd.read_csv(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Pipelines\national_hist_t_05-05.csv")

    overwrite_hist_column(forecast_path, hist_df, date_min, date_max)