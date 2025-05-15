import pandas as pd
import os
import plotly.graph_objects as go
import boto3
from utils_s3 import read_csv_from_s3, write_json_plot_to_s3

# Constants
BUCKET_NAME = "predi-conso-elec-region"
s3 = boto3.client("s3")

def plot_pred(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr):
    """
    Generate plot for full-day D+1 Prediction (from merged model outputs)

    """

    date_ymd = chosen_day.strftime("%Y-%m-%d")
    run_time_pred_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_ymd}/{run_time_hr}/pred"
    
    # Dynamically locate the CSV file
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=run_time_pred_folder_key + "/")
    prediction_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if "full" in os.path.basename(obj["Key"]) and obj ["Key"].endswith(".csv")
    ]

    if not prediction_files:
        print(f"⚠️ No full-day prediction found for run time {run_time_hr}.")
        return
    
    s3_key = prediction_files[0]
    df = read_csv_from_s3(s3_key)
    df["Datetime"] = pd.to_datetime(df["Datetime"])

    print(f"Creating tracer plot for region {region_abbr_caps} for {chosen_day} at runtime {run_time_hr}")

    # Initialize Plotly figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Datetime"],
        y=df["y_pred"],
        mode="lines",
        name="Consommation prévue",
        hovertemplate=
            "<b>Datetime</b>: %{x|%Y-%m-%d %H:%M}<br>" +
            "<b>Predicted</b>: %{y:.2f} MW<br>" +
            "<extra></extra>",
    ))

    # Vertical line that follows the cursor
    fig.update_layout(
        hovermode="x unified",  # aligns all traces on the same x
        width=900,
        height=400,
        title=f"{region_abbr_caps} - {date_ymd} - {run_time_hr} Run<br>Consommation prévue",
        xaxis=dict(showspikes=True, spikemode="across", spikesnap="cursor", showline=True),
        yaxis=dict(showline=True),
        margin=dict(l=50, r=50, t=60, b=40),
    )

    # Save to S3
    plot_filename = f"plot_pred_full_{region_abbr_lwrc}_{date_ymd}_{run_time_hr}.json"
    plot_key = f"{run_time_pred_folder_key}/{plot_filename}"
    plot_json = fig.to_json()
    write_json_plot_to_s3(plot_json, plot_key, content_type="application/json")

    print(f"✅ Plot saved for run_time {run_time_hr} to s3://{BUCKET_NAME}/{plot_key}")
