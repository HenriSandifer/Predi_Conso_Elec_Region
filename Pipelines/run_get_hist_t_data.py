from func_get_reg_hist_temp import fetch_station_measures
from utils_hist_t_data import prepare_df_t_hist, prepare_pipeline_inputs
import pandas as pd
import argparse

def get_hist_t_data(region, day, model, time):
    inputs = prepare_pipeline_inputs(region, day, model, time)
    
    stations = inputs["stations"]
    past_date = inputs["past_date"]
    chosen_day = inputs["chosen_day"]
    region_lwrc = inputs["region_abbr"]
    date_md = inputs["chosen_day"].strftime("%m-%d")

    print(f"STATIONS LOOKS LIKE : {stations}")
    
    # List to collect DataFrames for each station.
    dfs = []

    for station in stations:
        station_id = station["ID"]
        print(f"Fetching data for station {station['Nom']} (ID: {station_id}) for {past_date}...")
        df_station = fetch_station_measures(station_id, past_date)
        if df_station is not None:
            # Rename the temperature column to include the station name (or ID) for clarity.
            df_station.rename(columns={"t": f"t_{station_id}"}, inplace=True)
            dfs.append(df_station)

    if dfs:
        # Merge DataFrames from all stations on the "measured_at" timestamp.
        # We assume the timestamps are nearly aligned. We'll do an outer join and then align.
        df_merged = dfs[0]
        for df in dfs[1:]:
            df_merged = pd.merge_asof(df_merged.sort_values("measured_at"),
                                    df.sort_values("measured_at"),
                                    on="measured_at",
                                    tolerance=pd.Timedelta("15min"),
                                    direction="nearest")
        
        # Filter the merged DataFrame to only include rows that are common (or fill missing values as needed)
        # For simplicity, we drop rows with any missing temperature values:
        df_merged.dropna(inplace=True)
        
        # Compute the regional average temperature (row-wise average across the temperature columns).
        temp_columns = [col for col in df_merged.columns if col.startswith("t_")]
        df_merged["t_avg"] = df_merged[temp_columns].mean(axis=1)
        
        # Convert from Kelvin to Celsius if necessary:
        df_merged["t_avg"] = df_merged["t_avg"] - 273.15
            
    else:
        print("No weather data retrieved for the region.")

    df_t_hist = prepare_df_t_hist(chosen_day, df_merged, stations, region)
    df_t_hist.to_csv("temp_{}_{}_hist".format(region_lwrc, date_md), index=False)
    print(f"✅ Temp data csv successfully written for {region} prior to {chosen_day}")

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Chosen day (e.g., '2025-03-10')")
    parser.add_argument("--model", type=str, required=True, help="model (e.g., 'M48')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()
    get_hist_t_data(args.region, args.day, args.model, args.time)   