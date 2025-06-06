import pandas as pd
import unicodedata
from sklearn.metrics import (
    root_mean_squared_error,
    mean_absolute_error,
    r2_score
)

from src.utils.utils_s3 import read_csv_from_s3, write_csv_to_s3
from src.utils.utils_pred_eval_inputs import get_pred_eval_inputs

import boto3
import os

s3 = boto3.client("s3")
bucket_name = "predi-conso-elec-region"


def evaluate_model_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr):
    """
    Evaluates all individual model predictions for a given region/run_time/day.
    Saves evaluation CSVs and metrics to S3.
    
    """
    
    date_str = chosen_day.strftime("%Y-%m-%d")
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_hr}/pred"

    # Define full-day evaluation file path and check if it exists
    eval_filename_check = f"eval_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    run_time_eval_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_hr}/eval"
    eval_key_check = f"{run_time_eval_folder_key}/{eval_filename_check}"

    try:
        s3.head_object(Bucket=bucket_name, Key=eval_key_check)
        print(f"✋ Evaluation file already exists for {region} on {date_str} at {run_time_hr}, skipping.")
        return  # Skip evaluation
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise  # Raise other unexpected errors

    # 1. List relevant prediction files in S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=run_time_pred_folder_key + "/")
    prediction_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".csv") and "all_models" not in obj["Key"] and "pred_full" not in obj["Key"]
    ]

    if not prediction_files:
        print("⚠️ No individual model predictions found for this run time.")
        return

    # 2. Load real data
    real_data_key = "raw_data/real_cons_data.csv"
    df_real = read_csv_from_s3(real_data_key)
    df_real["Datetime"] = pd.to_datetime(df_real["Datetime"])

    # Normalize region
    normalized_region = unicodedata.normalize("NFKD", region)
    df_real = df_real[
        (df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region)
    ].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    metrics = []

    for s3_key in prediction_files:
        df_pred = read_csv_from_s3(s3_key)
        df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])

        filename = os.path.basename(s3_key)
        parts = filename.split("_")

        try:
            model_name = parts[3]
        except IndexError:
            print(f"⚠️ Could not parse model name from filename: {filename}")
            continue

        # Get time window for this model
        normalized_run_time = f"{int(run_time_hr):02d}:00:00"
        inputs = get_pred_eval_inputs(region, chosen_day.strftime("%Y-%m-%d"), model_name.upper(), normalized_run_time)
        start = inputs["first_row"]
        end = inputs["last_row"]

        df_real_window = df_real[(df_real["Datetime"] >= start) & (df_real["Datetime"] <= end)].copy()

        if df_real_window.empty:
            print(f"⚠️ No real data found for {model_name.upper()} timeframe.")
            continue

        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        df_eval = pd.merge(df_pred, df_real_window, on="Datetime", suffixes=("_pred", "_real"))

        # Compute metrics
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

        # Save the evaluation dataframe
        eval_filename = f"eval_{region_abbr_lwrc}_{model_name}_{date_str}_{run_time_hr}.csv"
        run_time_eval_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_hr}/eval"
        eval_key = f"{run_time_eval_folder_key}/{eval_filename}"
        write_csv_to_s3(df_eval, eval_key)

    # Save evaluation metrics summary
    metrics_df = pd.DataFrame(metrics)
    metrics_key = f"{run_time_eval_folder_key}/metrics_individual_models_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    write_csv_to_s3(metrics_df, metrics_key)

    print(f"✅ Individual model metrics saved to: s3://{bucket_name}/{metrics_key}")
