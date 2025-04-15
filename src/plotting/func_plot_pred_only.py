import pandas as pd
import os
import plotly.express as px
import boto3
from utils_s3 import read_csv_from_s3, write_csv_to_s3
from dictionaries import run_time_dict

s3 = boto3.client("s3")
bucket_name = "predi-conso-elec-region"

def plot_pred_only(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    
    """
    Generate plot for D+1 Prediction
    
    """
        
    run_time_str = run_time_dict.get(run_time_str)
    date_str = chosen_day.strftime("%Y-%m-%d")
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_str}/pred"

    # 1. List relevant prediction files in S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=run_time_pred_folder_key + "/")
    prediction_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".csv")
    ]

    if not prediction_files:
        print("⚠️ No individual model predictions found for this run time.")
        return

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

        # Add an if statement saying if "full" is in the name of the file, model_name = "Full Day Prediction"

        # Plot using Plotly
        fig = px.line(
            df_pred,
            x="Datetime",
            y="y_pred",
            title=f"{region_abbr_caps} - {chosen_day.strftime('%Y-%m-%d')} - {run_time_str} Run - {model_name} <br>Predicted Consumption (MW)",
            labels={"Datetime": "Time", "y_pred": "Predicted Consumption (MW)"}
        )

        fig.update_layout(
            width=900,
            height=400,
            margin=dict(l=50, r=50, t=60, b=40),
        )

    # Save the plot
    pred_filename = f"pred_{region_abbr_lwrc}_{model_name}_{date_str}_{run_time_str}.csv"
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_str}/pred"
    pred_key = f"{run_time_pred_folder_key}/{pred_filename}"
    write_csv_to_s3(df_pred, pred_key)
