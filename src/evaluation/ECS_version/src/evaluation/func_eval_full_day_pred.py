import pandas as pd
import unicodedata
from sklearn.metrics import (
    root_mean_squared_error,
    mean_absolute_error,
    r2_score
)

from src.utils.dictionaries import run_time_dict
from src.utils.utils_s3 import read_csv_from_s3, write_csv_to_s3
import boto3

s3 = boto3.client("s3")
bucket_name = "predi-conso-elec-region"


def evaluate_full_day_prediction(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr):
    """
    Evaluates the full-day prediction file (ALL_MODELS) for a given run_time.
    Saves merged eval file and metrics to S3.
    
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
      
    date_str = chosen_day.strftime("%Y-%m-%d")
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_hr}/pred"

    pred_filename = f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    pred_key = f"{run_time_pred_folder_key}/{pred_filename}"

    try:
        df_pred = read_csv_from_s3(pred_key)
    except Exception as e:
        print(f"⚠️ Could not load full-day prediction file: {pred_key}\n{e}")
        return

    df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])

    # Load and filter real data
    real_data_key = "raw_data/real_cons_data.csv"
    df_real = read_csv_from_s3(real_data_key)
    df_real["Datetime"] = pd.to_datetime(df_real["Datetime"])

    normalized_region = unicodedata.normalize("NFKD", region)
    df_real = df_real[
        (df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region)
    ].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    # Filter real data to target day
    df_real_day = df_real[df_real["Datetime"].dt.date == chosen_day.date()].copy()

    if df_real_day.empty:
        print(f"⚠️ No real data found for full-day evaluation on {date_str}.")
        return

    df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
    df_eval = pd.merge(df_pred, df_real_day, on="Datetime", suffixes=("_pred", "_real"))

    # Compute metrics
    mae = mean_absolute_error(df_eval["y_real"], df_eval["y_pred"])
    rmse = root_mean_squared_error(df_eval["y_real"], df_eval["y_pred"])
    r2 = r2_score(df_eval["y_real"], df_eval["y_pred"])
    mean_consumption = df_eval["y_real"].mean()

    metrics = [{
        "Model": "ALL_MODELS",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE / Mean": mae / mean_consumption,
        "RMSE / Mean": rmse / mean_consumption
    }]

    # Save the evaluation CSV
    eval_filename = f"eval_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    run_time_eval_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_hr}/eval" 
    eval_key = f"{run_time_eval_folder_key}/{eval_filename}"
    write_csv_to_s3(df_eval, eval_key)

    # Append metrics to the same file as others (overwrite ok)
    metrics_df = pd.DataFrame(metrics)
    metrics_key = f"{run_time_eval_folder_key}/metrics_individual_models_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"

    try:
        # Try reading existing metrics and append to it
        existing_df = read_csv_from_s3(metrics_key)
        combined_df = pd.concat([existing_df, metrics_df], ignore_index=True)
    except Exception:
        # No existing metrics file — just use new
        combined_df = metrics_df

    write_csv_to_s3(combined_df, metrics_key)

    print(f"✅ Full-day prediction evaluation and metrics saved to: s3://{bucket_name}/{run_time_eval_folder_key}")
