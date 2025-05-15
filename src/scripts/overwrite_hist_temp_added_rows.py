import os
import pandas as pd
from datetime import datetime

def overwrite_hist_column(forecast_path, hist_df, date_min, date_max):
    df_forecast = pd.read_csv(forecast_path)
    df_forecast["Datetime"] = pd.to_datetime(df_forecast["Datetime"])
    hist_df["Datetime"] = pd.to_datetime(hist_df["Datetime"])

    # Filter for relevant range
    hist_range = hist_df[(hist_df["Datetime"] >= date_min) & (hist_df["Datetime"] <= date_max)]

    # Identify missing rows (Datetime + Région) in forecast
    forecast_keys = set(zip(df_forecast["Datetime"], df_forecast["Région"]))
    hist_keys = set(zip(hist_range["Datetime"], hist_range["Région"]))

    missing_keys = hist_keys - forecast_keys
    print(f"➕ Adding {len(missing_keys)} missing rows to forecast...")

    if missing_keys:
        missing_df = pd.DataFrame(list(missing_keys), columns=["Datetime", "Région"])
        df_forecast = pd.concat([df_forecast, missing_df], ignore_index=True)

    # Merge historical values onto forecast
    df_forecast = df_forecast.merge(
        hist_range[["Datetime", "Région", "t"]],
        on=["Datetime", "Région"],
        how="left",
        suffixes=("", "_new")
    )

    # Overwrite or fill in hist_t using merged values
    date_mask = (df_forecast["Datetime"] >= date_min) & (df_forecast["Datetime"] <= date_max)
    df_forecast.loc[date_mask, "hist_t"] = df_forecast.loc[date_mask, "t"]
    df_forecast.drop(columns=["t"], inplace=True)

    # Sort by Datetime then Region for readability
    df_forecast.sort_values(by=["Datetime", "Région"], inplace=True)

    # Save updated file
    df_forecast.to_csv(forecast_path, index=False)
    print(f"✅ Forecast file updated and missing timestamps inserted.")


if __name__ == "__main__":
    hist_folder = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Pipelines"
    forecast_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\s3_downloaded_datasets\temperature_forecast_data.csv"
    merged_hist_path = os.path.join(hist_folder, "national_hist_t_05-05.csv")

    date_min = datetime(2025, 4, 5, 0, 0)
    date_max = datetime(2025, 5, 5, 23, 45)

    hist_df = pd.read_csv(merged_hist_path)

    overwrite_hist_column(forecast_path, hist_df, date_min, date_max)
