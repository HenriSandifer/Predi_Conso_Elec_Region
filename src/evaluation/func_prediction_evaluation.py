import pandas as pd
from datetime import datetime, timedelta
from utils.dictionaries import (weather_stations, region_abbr_dict,
                                 region_abbr_caps_dict, run_time_dict,
                                   model_delta, holiday_zones,
                                     prediction_timeframes,
                                       models_by_run_time,
                                         lag_roll_features_by_model,
                                           lag_feature_multipliers_by_model,
                                             roll_feature_multipliers)
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import (root_mean_squared_error,
                             mean_absolute_error, r2_score)
import unicodedata

from src.evaluation.utils_pred_eval_inputs import get_pred_eval_inputs

def evaluate_all_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    date_str = chosen_day.strftime("%Y-%m-%d")
    base_dir = "Predictions"
    run_time_folder = os.path.join(base_dir, region_abbr_caps, str(target_month), date_str, str(run_time_str))

    # Gather CSV files
    prediction_files = [
        os.path.join(run_time_folder, f)
        for f in os.listdir(run_time_folder)
        if f.endswith(".csv") and "all_models" not in f  # Avoid reloading concatenated full-day prediction
    ]

    if not prediction_files:
        print("⚠️ No prediction files found for this run time.")
        return

    df_real = pd.read_csv(
        r"C:\\Users\\Henri\\Documents\\GitHub\\Predi_Conso_Elec_Region\\data\\cons_temp_2025.csv",
        parse_dates=['Datetime']
    )
    normalized_region = unicodedata.normalize("NFKD", region)
    df_real = df_real[
        (df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region)
    ].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    metrics = []
    full_day_df = []

    for file in prediction_files:
        df_pred = pd.read_csv(file, parse_dates=["Datetime"])
        
        filename = os.path.basename(file)
        parts = filename.split("_")

        try:
            model_name = parts[3]  # "M36", "M18", etc.
        except IndexError:
            print(f"⚠️ Could not parse model name from filename: {filename}")
            continue


        # Prepare model-specific time window

        # Normalize run_time_str from "2" to "02:00:00"
        normalized_run_time = f"{int(run_time_str):02d}:00:00"

        inputs = get_pred_eval_inputs(region, chosen_day.strftime("%Y-%m-%d"), model_name.upper(), normalized_run_time)
        start = inputs["first_row"]
        end = inputs["last_row"]

        # Filter real
        df_real_window = df_real[(df_real['Datetime'] >= start) & (df_real['Datetime'] <= end)].copy()

        if df_real_window.empty:
            print(f"⚠️ No real data found for {model_name.upper()} timeframe.")
            continue

        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        df_eval = pd.merge(df_pred, df_real_window, on="Datetime", suffixes=("_pred", "_real"))

        mae = mean_absolute_error(df_eval["y_real"], df_eval["y_pred"])
        rmse = root_mean_squared_error(df_eval["y_real"], df_eval["y_pred"])
        r2 = r2_score(df_eval["y_real"], df_eval["y_pred"])
        mean_consumption = df_eval["y_real"].mean()

        metrics.append({
            "Model": model_name.upper(),
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
            "MAE / Mean": mae / mean_consumption,
            "RMSE / Mean": rmse / mean_consumption
        })

        full_day_df.append(df_pred)

    # Full day concatenation
    df_pred_full = pd.read_csv() ### GET IN THERE 
    df_real_day = df_real[df_real['Datetime'].dt.date == chosen_day.date()].copy()
    df_eval_full = pd.merge(df_pred_full, df_real_day, on="Datetime")

    # Save df_real_day to CSV for future use for plotting
    real_cons_path = os.path.join(run_time_folder, f"real_cons_{region_abbr_lwrc}_{date_str}.csv")
    df_real_day.to_csv(real_cons_path, index=False)

    # Define metrics
    mae = mean_absolute_error(df_eval_full["y_real"], df_eval_full["y_pred"])
    rmse = root_mean_squared_error(df_eval_full["y_real"], df_eval_full["y_pred"])
    r2 = r2_score(df_eval_full["y_real"], df_eval_full["y_pred"])
    mean_consumption = df_eval_full["y_real"].mean()

    metrics.append({
        "Model": "ALL_MODELS",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE / Mean": mae / mean_consumption,
        "RMSE / Mean": rmse / mean_consumption
    })

    # Save metrics
    metrics_df = pd.DataFrame(metrics)
    metrics_path = os.path.join(run_time_folder, f"evaluation_metrics_{region_abbr_lwrc}_{date_str}_{run_time_str}.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"📊 Metrics saved to: {metrics_path}")