import pandas as pd
import plotly.graph_objects as go
from utils_s3 import read_csv_from_s3, write_json_plot_to_s3

# Constants
BUCKET_NAME = "predi-conso-elec-region"
RUN_TIMES = ["2", "8", "14", "20"]

def plot_eval(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day):
    """
    Loops through each run_time for the chosen_day, retrieves full-day evaluation,
    and saves an interactive plot to S3 with custom hovertext and cursor tracer.
    """

    date_str = chosen_day.strftime("%Y-%m-%d")

    for rt in RUN_TIMES:
        run_time_eval_folder_key = f"Predictions/{region_abbr_caps}/{target_month}/{date_str}/{rt}/eval"
        eval_filename = f"eval_full_{region_abbr_lwrc}_{date_str}_{rt}.csv"
        eval_key = f"{run_time_eval_folder_key}/{eval_filename}"

        try:
            df = read_csv_from_s3(eval_key)
        except Exception as e:
            print(f"⚠️ Could not read {eval_filename}: {e}")
            continue

        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df["delta"] = df["y_real"] - df["y_pred"]
        df["perc_diff"] = 100 * df["delta"] / df["y_real"]
        df["perc_diff"] = df["perc_diff"].round(2)

        fig = go.Figure()

        # Real Consumption trace
        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["y_real"],
            mode="lines",
            name="Real Consumption",
            hovertemplate=
                "<b>Datetime</b>: %{x|%Y-%m-%d %H:%M}<br>" +
                "<b>Real</b>: %{y:.2f} MW<br>" +
                "<extra></extra>",
        ))

        # Predicted Consumption trace with delta & % diff in hover
        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["y_pred"],
            mode="lines",
            name="Predicted Consumption",
            hovertemplate=
                "<b>Datetime</b>: %{x|%Y-%m-%d %H:%M}<br>" +
                "<b>Predicted</b>: %{y:.2f} MW<br>" +
                "<b>Δ (MW)</b>: %{customdata[0]:.2f}<br>" +
                "<b>% diff</b>: %{customdata[1]:.2f}%<br>" +
                "<extra></extra>",
            customdata=df[["delta", "perc_diff"]].values
        ))

        # Vertical line that follows the cursor
        fig.update_layout(
            hovermode="x unified",  # aligns all traces on the same x
            width=900,
            height=400,
            title=f"{region_abbr_caps} - {date_str} - {rt} Run<br>Prediction vs. Real Consumption",
            xaxis=dict(showspikes=True, spikemode="across", spikesnap="cursor", showline=True),
            yaxis=dict(showline=True),
            margin=dict(l=50, r=50, t=60, b=40),
        )

        # Save to S3
        plot_filename = f"plot_eval_full_{region_abbr_lwrc}_{date_str}_{rt}.json"
        plot_key = f"{run_time_eval_folder_key}/{plot_filename}"
        plot_json = fig.to_json()
        write_json_plot_to_s3(plot_json, plot_key, content_type="application/json")

        print(f"✅ Plot saved for run_time {rt} to s3://{BUCKET_NAME}/{plot_key}")
