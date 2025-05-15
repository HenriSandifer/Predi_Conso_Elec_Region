import pandas as pd
import plotly.express as px
from utils_s3 import read_csv_from_s3, write_json_plot_to_s3

# Constants
BUCKET_NAME = "predi-conso-elec-region"
RUN_TIMES = ["2", "8", "14", "20"]

def plot_eval(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day):
    """
    Loops through each run_time for the chosen_day, retrieves full-day evaluation,
    and saves an interactive plot to S3.
    
    """

    date_str = chosen_day.strftime("%Y-%m-%d")

    for rt in RUN_TIMES:
                
        run_time_eval_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{rt}/eval"
        eval_filename = f"eval_full_{region_abbr_lwrc}_{date_str}_{rt}.csv"
        eval_key = f"{run_time_eval_folder_key}/{eval_filename}"

        try:
            df_eval = read_csv_from_s3(eval_key)
        except Exception as e:
            print(f"⚠️ Could not read {eval_filename}: {e}")
            continue

        df_eval["Datetime"] = pd.to_datetime(df_eval["Datetime"])

        # Plot with Plotly
        df_plot = df_eval.rename(columns={
        "y_real": "Real Consumption",
        "y_pred": "Predicted Consumption"
        })

        df_plot_long = df_plot.melt(id_vars="Datetime", value_vars=["Real Consumption", "Predicted Consumption"])

        fig = px.line(
            df_plot_long,
            x="Datetime",
            y="value",
            color="variable",
            title=f"{region_abbr_caps} - {date_str} - {rt} Run<br>Prediction vs. Real Consumption",
            labels={"value": "Consumption (MW)", "variable": "Legend"},
        )

        fig.update_layout(
            width=900,
            height=400,
            margin=dict(l=50, r=50, t=60, b=40),
        )

        # Save to S3 as interactive plot
        plot_filename = f"plot_eval_full_{region_abbr_lwrc}_{date_str}_{rt}.json"
        plot_key = f"{run_time_eval_folder_key}/{plot_filename}"
        plot_json = fig.to_json()
        write_json_plot_to_s3(plot_json, plot_key, content_type="application/json")

        print(f"✅ Plot saved for run_time {rt} to s3://{BUCKET_NAME}/{plot_key}")
