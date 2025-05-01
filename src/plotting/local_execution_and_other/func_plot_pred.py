import pandas as pd
import os
import plotly.express as px
import boto3
from utils_s3 import read_csv_from_s3, write_plot_to_s3

s3 = boto3.client("s3")
bucket_name = "predi-conso-elec-region"

def plot_pred(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    
    """
    Generate plot for full-day D+1 Prediction (from merged model outputs)
    
    """

    date_str = chosen_day.strftime("%Y-%m-%d")
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{run_time_str}/pred"

    # List only the full-day prediction file
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=run_time_pred_folder_key + "/")
    prediction_files = [
        
        obj["Key"]
        for obj in response.get("Contents", [])
        if "full" in os.path.basename(obj["Key"]) and obj["Key"].endswith(".csv")
    ]
   
    if not prediction_files:
        print("⚠️ No full-day prediction found for run time {}.")
        return

    # Assuming one full-day prediction fil per run_time
    s3_key = prediction_files[0]
    df_pred = read_csv_from_s3(s3_key)
    df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])

    # Plot using Plotly
    fig = px.line(
        df_pred,
        x="Datetime",
        y="y_pred",
        title=f"{region_abbr_caps} - {date_str} - {run_time_str} Run <br>Full Day Prediction",
        labels={"Datetime": "Time", "y_pred": "Predicted Consumption (MW)"}
    )

    fig.update_layout(
        width=900,
        height=400,
        margin=dict(l=50, r=50, t=60, b=40),
    )

    # Save the plot
    plot_filename = f"plot_full_pred_{region_abbr_lwrc}_{date_str}_{run_time_str}.html"
    plot_key = f"{run_time_pred_folder_key}/{plot_filename}"
            
    write_plot_to_s3(fig, plot_key)
    print(f"✅ Saved full-day prediction plot to s3://{bucket_name}/{plot_key}")
