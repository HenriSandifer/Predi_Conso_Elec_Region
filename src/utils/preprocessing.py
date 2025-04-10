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


def create_prediction_output_folder(region_abbr_caps, target_month, target_day, run_time_str):
    """
    Creates a folder structure: Predictions/REGION/Month/YYYY-MM-DD/HH:MM/
    Returns the full path to the run_time folder.
    """
    base_dir = "Predictions"
    date_folder = target_day.strftime("%Y-%m-%d")  # e.g., 2025-03-12
    run_time_folder = str(run_time_str)  # e.g., "02:00"
    month_folder = str(target_month)
    full_path = os.path.join(base_dir, region_abbr_caps, month_folder, date_folder, run_time_folder)

    os.makedirs(full_path, exist_ok=True)
    return full_path