from src.func_single_prediction import run_pipeline_for_model
from src.dictionaries import (models_by_run_time,
                          region_abbr_caps_dict,
                           run_time_dict,
                           region_abbr_dict)
from src.utils_s3 import read_csv_from_s3, write_csv_to_s3
from src.utils_preprocessing import create_prediction_output_key
import pandas as pd
import boto3

def run_all_models_for_time(region, chosen_day, run_time_hms):
    """
    Runs all models for a given region, target day, and run time.

    Saves CSV of concatenated prediction for run_time

    """

    region_abbr_caps = region_abbr_caps_dict.get(region, "NA")
    target_month = pd.to_datetime(chosen_day).strftime("%Y-%m")
    run_time_hr = run_time_dict.get(run_time_hms, "NA")
    region_abbr_lwrc = region_abbr_dict.get(region, "NA")
    
    models_to_run = models_by_run_time[run_time_hms]
    
    for model in models_to_run:
        print(f"⌛ Running {model} model...")
        run_pipeline_for_model(region, chosen_day, run_time_hms, model)

    ### Saving full day prediction of given run_time
    date_str = pd.to_datetime(chosen_day).strftime("%Y-%m-%d")
    bucket_name = "predi-conso-elec-region"
    run_time_folder_key = create_prediction_output_key(
        region_abbr_caps,
        target_month,
        chosen_day,
        run_time_hr)

    # Gather CSV files
    s3 = boto3.client("s3")

    # List objects inside the run_time folder on S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=run_time_folder_key + "/")
    
    prediction_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".csv") and "all_models" not in obj["Key"]
    ]

    if not prediction_files:
        print("⚠️ No prediction files found for this run time.")
        return

    full_day_df = []

    for s3_key in prediction_files:
        df_pred = read_csv_from_s3(s3_key)
        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        full_day_df.append(df_pred)

    # Full day concatenation
    df_pred_full = pd.concat(full_day_df).sort_values("Datetime")

    # Save df_pred_full to CSV for later evaluation and plotting
    pred_filename = f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    pred_key = f"{run_time_folder_key}/{pred_filename}"
    write_csv_to_s3(df_pred_full, pred_key)
    print(f"✅ Added full-day prediction for {region_abbr_caps} run_time {run_time_hms} on {chosen_day} to S3.")