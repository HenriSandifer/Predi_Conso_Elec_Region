import pandas as pd
from datetime import datetime, timedelta
from dictionaries import weather_stations, region_abbr_dict, region_abbr_caps_dict, run_time_dict, model_delta, holiday_zones, prediction_timeframes

# Define your function early on (in one cell)
def prepare_pipeline_inputs(region: str, chosen_day_str: str, model: str, run_time: str):
    
    # Parse chosen day as datetime
    chosen_day = datetime.strptime(chosen_day_str, "%Y-%m-%d")

    # Region
    Région = region
       
    # Build consumption API where clause for the 5 days prior
    num_days = 6
    consumption_dates = [(chosen_day - timedelta(days=i)).strftime("%Y-%m-%d") 
                         for i in range(num_days, 0, -1)]
    
    consumption_where = f'libelle_region:"{region}" AND (' + " OR ".join(
        f'date:"{d}"' for d in consumption_dates
    ) + ')'
    
    # Build consumption API where clause for the past, target, and next day
    num_days = 3
    consumption_dates_2 = [(chosen_day + timedelta(days=i-1)).strftime("%Y-%m-%d") 
                         for i in range(num_days)]
    
    consumption_where_2 = f'libelle_region:"{region}" AND (' + " OR ".join(
        f'date:"{d}"' for d in consumption_dates_2
    ) + ')'

    # For temperature API, target date is 5 days before chosen day
    past_date = (chosen_day - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Load weather stations from a dictionary file (assumes file "weather_stations.dict" exists)
    stations = weather_stations.get(region, [])
        
    # Look up the timeframe for the given model/run_time pair
    timeframe = prediction_timeframes.get((model, run_time))
    if timeframe is None:
        raise ValueError(f"No timeframe defined for model {model} at run time {run_time}")
    
    # Build start and end datetime objects using chosen_day's date.
    start_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["start"], "%H:%M:%S").time())
    end_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["end"], "%H:%M:%S").time())

    # Create the expected timestamps for the prediction placeholder
    expected_timestamps = pd.date_range(start=start_dt, end=end_dt, freq="15min")

    delta = model_delta.get(model)

    deltatime = timedelta(hours=delta)

    # Dictionary for region abbreviations
    region_abbr = region_abbr_dict.get(region, "NA")

   #Dictionary for capitalized region abbreviations
    region_abbr_caps = region_abbr_caps_dict.get(region, "NA")

    #Dictionary for run_time abbreviations
    run_time_abbr = run_time_dict.get(run_time, "NA")
   
    return {
        "chosen_day": chosen_day,
        "consumption_where": consumption_where,
        "consumption_dates": consumption_dates,
        "past_date": past_date,
        "stations": stations,
        "region_abbr": region_abbr,
        "region_caps": region_abbr_caps,
        "region": Région,
        "consumption_where_2": consumption_where_2,
        "consumption_dates_2": consumption_dates_2,
        "model": delta,
        "run_time": run_time,
        "run_time_abbr": run_time_abbr,
        "prediction_timestamps": expected_timestamps,
        "first_row": start_dt,
        "last_row": end_dt,
        "deltatime": deltatime
    }

def prepare_df_t_hist(chosen_day, df_merged, stations, region):
    print(f"DF_MERGED COLUMNS LOOK LIKE : {df_merged.columns}")

    temp_hist_dates = [((chosen_day - timedelta(days=i)).month, 
                        (chosen_day - timedelta(days=i)).day)
                       for i in range(30, 0, -1)]

    df_temp_hist = df_merged[
        (df_merged['measured_at'].dt.year == chosen_day.year) &
        (df_merged['measured_at'].dt.month.isin([m for m, d in temp_hist_dates])) &
        (df_merged['measured_at'].dt.day.isin([d for m, d in temp_hist_dates]))
    ].copy()

    # Sanity print
    print("✅ Filtering complete. Columns:", df_temp_hist.columns)

    # Ensure 'measured_at' is datetime
    df_temp_hist["measured_at"] = pd.to_datetime(df_temp_hist["measured_at"])

    # 🔁 PREVENT NAME CONFLICT: Rename the column BEFORE making it index
    df_temp_hist.rename(columns={"measured_at": "Datetime"}, inplace=True)

    # Drop any lingering "Datetime" column that might cause conflict
    if "Datetime" in df_temp_hist.columns:
        print("⚠️ Dropping pre-existing 'Datetime' column to avoid conflict")
        df_temp_hist.drop(columns=["Datetime"], inplace=True)

    # Set index to 'Datetime'
    df_temp_hist["Datetime"] = pd.to_datetime(df_merged["measured_at"])
    df_temp_hist.set_index("Datetime", inplace=True)

    print("✅ Index set to 'Datetime'. Columns now:", df_temp_hist.columns)

    # Resample and interpolate
    df_temp_hist = df_temp_hist.resample("15min").interpolate(method="linear")

    # Reset index safely
    df_temp_hist.reset_index(inplace=True)
    print("✅ Index reset. Columns:", df_temp_hist.columns)


    print("✅ After full reset. Columns:", df_temp_hist.columns)

    # Filter again to keep only the 30 days prior
    temp_hist_dates_subset = [((chosen_day - timedelta(days=i)).month,
                               (chosen_day - timedelta(days=i)).day)
                              for i in range(30, 0, -1)]

    df_t_hist = df_temp_hist[
        (df_temp_hist['Datetime'].dt.month.isin([m for m, d in temp_hist_dates_subset])) &
        (df_temp_hist['Datetime'].dt.day.isin([d for m, d in temp_hist_dates_subset]))
    ].copy()

    # Drop station columns and rename t_avg
    drop_columns = [f"t_{station['ID']}" for station in stations]
    print(f"DROP_COLUMNS LOOKS LIKE : {drop_columns}")
    print(f"DF_T_HIST COLUMNS BEFORE DROPPING : {df_t_hist.columns}")

    df_t_hist.drop(columns=drop_columns, inplace=True, errors="ignore")
    df_t_hist.rename(columns={"t_avg": "t"}, inplace=True)
    df_t_hist["Région"] = region

    print(f"✅ Final columns: {df_t_hist.columns}")
    return df_t_hist
