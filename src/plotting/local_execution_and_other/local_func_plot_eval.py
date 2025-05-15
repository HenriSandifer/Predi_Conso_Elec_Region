import os
import pandas as pd
import plotly.graph_objects as go

# Constants
RUN_TIMES = ["2", "8", "14", "20"]
LOCAL_BASE_DIR = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"

def plot_eval(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day):
    """
    Loops through each run_time for the chosen_day, retrieves full-day evaluation CSV,
    and saves an interactive plot as a JSON file to the local eval folder — but only if not already present.
    """

    date_str = chosen_day.strftime("%Y-%m-%d")

    for rt in RUN_TIMES:
        eval_folder = os.path.join(
            LOCAL_BASE_DIR,
            region_abbr_caps,
            target_month,
            date_str,
            rt,
            "eval"
        )

        eval_filename = f"eval_full_{region_abbr_lwrc}_{date_str}_{rt}.csv"
        eval_path = os.path.join(eval_folder, eval_filename)

        plot_filename = f"plot_eval_full_{region_abbr_lwrc}_{date_str}_{rt}.json"
        plot_path = os.path.join(eval_folder, plot_filename)

        # Skip if plot already exists
        if os.path.exists(plot_path):
            print(f"⏭️ Plot already exists: {plot_path} — skipping")
            continue

        # Skip if evaluation CSV doesn't exist
        if not os.path.exists(eval_path):
            print(f"⚠️ Eval CSV not found: {eval_path}")
            continue

        try:
            df = pd.read_csv(eval_path)
        except Exception as e:
            print(f"⚠️ Failed to read {eval_filename}: {e}")
            continue

        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df["delta"] = df["y_real"] - df["y_pred"]
        df["perc_diff"] = 100 * df["delta"] / df["y_real"]
        df["perc_diff"] = df["perc_diff"].round(2)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["y_real"],
            mode="lines",
            name="Real Consumption",
            hovertemplate="<b>Datetime</b>: %{x|%Y-%m-%d %H:%M}<br><b>Real</b>: %{y:.2f} MW<br><extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=df["Datetime"],
            y=df["y_pred"],
            mode="lines",
            name="Predicted Consumption",
            hovertemplate=(
                "<b>Datetime</b>: %{x|%Y-%m-%d %H:%M}<br>"
                "<b>Predicted</b>: %{y:.2f} MW<br>"
                "<b>Δ (MW)</b>: %{customdata[0]:.2f}<br>"
                "<b>% diff</b>: %{customdata[1]:.2f}%<br><extra></extra>"
            ),
            customdata=df[["delta", "perc_diff"]].values
        ))

        fig.update_layout(
            hovermode="x unified",
            width=900,
            height=400,
            title=f"{region_abbr_caps} - {date_str} - {rt} Run<br>Prediction vs. Real Consumption",
            xaxis=dict(showspikes=True, spikemode="across", spikesnap="cursor", showline=True),
            yaxis=dict(showline=True),
            margin=dict(l=50, r=50, t=60, b=40),
        )

        fig.write_json(plot_path)
        print(f"✅ Plot saved: {plot_path}")
