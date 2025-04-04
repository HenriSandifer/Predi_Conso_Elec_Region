
import pandas as pd
from datetime import datetime, timedelta
from dictionaries import weather_stations, region_abbr_dict, region_abbr_caps_dict, run_time_dict, model_delta, holiday_zones, prediction_timeframes, models_by_run_time, lag_roll_features_by_model, lag_feature_multipliers_by_model, roll_feature_multipliers
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import unicodedata

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
    target_date = (chosen_day - timedelta(days=5)).strftime("%Y-%m-%d")
    
    # Load weather stations from a dictionary file (assumes file "weather_stations.dict" exists)
    stations_for_region = weather_stations.get(region, [])
       
    # Look up the timeframe for the given model/run_time pair
    timeframe = prediction_timeframes.get((model, run_time))
    if timeframe is None:
        raise ValueError(f"No timeframe defined for model {model} at run time {run_time}")
    
    # Build start and end datetime objects using chosen_day's date.
    start_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["start"], "%H:%M:%S").time())
    end_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["end"], "%H:%M:%S").time())

    # Create the expected timestamps for the prediction placeholder
    expected_timestamps = pd.date_range(start=start_dt, end=end_dt, freq="15min")

    #Gets 
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
        "target_date": target_date,
        "stations_for_region": stations_for_region,
        "region_abbr": region_abbr,
        "region_caps": region_abbr_caps,
        "Région": Région,
        "consumption_where_2": consumption_where_2,
        "consumption_dates_2": consumption_dates_2,
        "model_antic": delta,
        "run_time": run_time,
        "run_time_abbr": run_time_abbr,
        "prediction_timestamps": expected_timestamps,
        "first_row": start_dt,
        "last_row": end_dt,
        "deltatime": deltatime,
        "func_model": model
    }

def add_holiday_column(df_test, cons_temp_df):
    # 1. Map regions to zones
    df_test = df_test.copy()  # Work on a copy to avoid modifying the original
    
    cons_temp_df
    df_test["Zone"] = cons_temp_df["Région"].map(holiday_zones)
    
    # 2. Handle missing zones
    df_test["Zone"] = df_test["Zone"].fillna("Unknown")
    
    # 3. Precompute holidays for unique date-zone pairs
    date_zones = df_test[["Datetime", "Zone"]].drop_duplicates()
    holiday_checker = SchoolHolidayDates()
    
    date_zones["Holiday"] = date_zones.apply(
        lambda x: holiday_checker.is_holiday_for_zone(
            x["Datetime"].date(),
            x["Zone"]
        ) if x["Zone"] != "Unknown" else False,
        axis=1
    )
    
    # 4. Merge back into main DataFrame
    return df_test.merge(date_zones, on=["Datetime", "Zone"])


def apply_lag_roll_features(df_test, cons_temp_df, inputs):
    model_antic = inputs["model_antic"]
    deltatime = inputs["deltatime"]
    first_row = inputs["first_row"]
    last_row = inputs["last_row"]
    func_model = inputs["func_model"]

    lag_roll_features = lag_roll_features_by_model.get(func_model, [])

    # Ensure timezone-neutral
    cons_temp_df["Datetime"] = pd.to_datetime(cons_temp_df["Datetime"]).dt.tz_localize(None)

    for feature in lag_roll_features:
        if "rolling" in feature:
            # Compute rolling feature globally before slicing
            window = roll_feature_multipliers[feature]
            cons_temp_df[feature] = cons_temp_df["Consommation (MW)"].rolling(window=window).mean()

            # Match datetime with deltatime shift
            dt_start = first_row - deltatime
            dt_end = last_row - deltatime
            df_filtered = cons_temp_df[(cons_temp_df['Datetime'] >= dt_start) & (cons_temp_df['Datetime'] <= dt_end)]
            df_test[feature] = df_filtered[feature].values

        elif "lag" in feature:
            # Use model-specific multipliers
            model_lag_dict = lag_feature_multipliers_by_model.get(func_model, {})
            lag_hours = model_lag_dict.get(feature, ())
            lagged_timestamps = df_test["Datetime"] - timedelta(hours=lag_hours)  # or use seconds * multiplier
            df_filtered = cons_temp_df[cons_temp_df["Datetime"].isin(lagged_timestamps)]
            df_test[feature] = df_filtered["Consommation (MW)"].values
        

    return df_test


def create_prediction_output_folder(region_abbr_caps, target_day, run_time_str):
    """
    Creates a folder structure: Predictions/REGION/YYYY-MM-DD/HH:MM/
    Returns the full path to the run_time folder.
    """
    base_dir = "Predictions"
    date_folder = target_day.strftime("%Y-%m-%d")  # e.g., 2025-03-12

    run_time_folder = str(run_time_str)  # e.g., "02:00"
    full_path = os.path.join(base_dir, region_abbr_caps, date_folder, run_time_folder)

    os.makedirs(full_path, exist_ok=True)
    return full_path


def evaluate_all_predictions(region_abbr_caps, region_abbr_lwrc, chosen_day, run_time_str, func_region):
    """
    Concatenates prediction CSVs for a given run_time, evaluates them against real values,
    saves the concatenated prediction, and optionally plots/saves the plot.
    """
    # Folder setup
    date_str = str(chosen_day.strftime("%Y-%m-%d"))
    base_dir = "Predictions"
    run_time_folder = os.path.join(base_dir, region_abbr_caps, date_str, str(run_time_str))
    

    # Get all CSV files in the run_time folder
    prediction_files = [
        os.path.join(run_time_folder, f)
        for f in os.listdir(run_time_folder)
        if f.endswith(".csv")
    ]


    if not prediction_files:
        print("⚠️ No prediction files found for this run time.")
        return

    # Concatenate predictions
    dfs = [pd.read_csv(f, parse_dates=["Datetime"]) for f in prediction_files]
    df_pred = pd.concat(dfs).sort_values("Datetime")

    # Save concatenated predictions
    concat_filename = f"pred_cons_{region_abbr_lwrc}_all_models_{run_time_str}D0_{chosen_day.strftime('%m-%d')}.csv"
    concat_path = os.path.join(run_time_folder, concat_filename)
    df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
    df_pred.to_csv(concat_path, index=False)
    print(f"✅ Concatenated prediction saved to: {concat_path}")

    # Load real values for each model
    df_real = pd.read_csv(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predi_Conso_Elec_Region\data\cons_temp_2025.csv", parse_dates=['Datetime'])

    # Normalize func_region to match data encoding
    normalized_region = unicodedata.normalize("NFKD", func_region)
    
    # Ensure chosen_day is a date object
    if hasattr(chosen_day, 'date'):
        chosen_day = chosen_day.date()

    # Filter using normalized region and date
    df_real = df_real[
        (df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region) &
        (df_real["Datetime"].dt.date == chosen_day)
    ].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    if df_real.empty:
        print(f"⚠️ No real data found for {normalized_region} on {chosen_day}.")
        return


    # Merge predictions with real data
    df_eval = pd.merge(df_pred, df_real, on="Datetime", suffixes=("_pred", "_real"))

    # Evaluate
    mae = mean_absolute_error(df_eval["y_real"], df_eval["y_pred"])
    rmse = root_mean_squared_error(df_eval["y_real"], df_eval["y_pred"])
    r2 = r2_score(df_eval["y_real"], df_eval["y_pred"])

    print(f"\n📊 Evaluation Metrics for {region_abbr_caps} | {chosen_day} | {run_time_str} Run:")
    print(f"MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.2f}")

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(df_eval["Datetime"], df_eval["y_real"], label="Real", linewidth=2)
    plt.plot(df_eval["Datetime"], df_eval["y_pred"], label="Predicted", linestyle="--")
    plt.title(f"{region_abbr_caps} - {chosen_day} - {run_time_str} D0 Run\nPredicted vs Real Consumption")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plot_path = os.path.join(run_time_folder, f"prediction_plot_{region_abbr_lwrc}_{run_time_str}.png")
    plt.savefig(plot_path)
    print(f"📈 Plot saved to: {plot_path}")

    # If running from terminal or script, comment this out
    # plt.show()
