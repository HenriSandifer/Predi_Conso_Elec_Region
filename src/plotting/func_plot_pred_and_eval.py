import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

def plot_pred_and_eval(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    
    """
    Generate plot for D+1 Prediction + Real Data
    
    """
    
    # Setup
    base_dir = "Predictions"
    run_times = ["2", "8", "14", "20"]
    date_str = chosen_day.strftime("%Y-%m-%d")

    # Read the real consumption data (only once)
    real_data_path = os.path.join(
        base_dir, region_abbr_caps, str(target_month), date_str,
        f"real_cons_{region_abbr_lwrc}_{date_str}.csv"
    )
    df_real = pd.read_csv(real_data_path)

    # Dictionary to hold merged DataFrames
    df_merged = {}

    for rt in run_times:
        run_time_folder = os.path.join(base_dir, region_abbr_caps, str(target_month), date_str, rt)
        pred_filename = f"pred_full_{region_abbr_lwrc}_{date_str}_{rt}.csv"
        pred_path = os.path.join(run_time_folder, pred_filename)

        if not os.path.exists(pred_path):
            print(f"⚠️ Prediction file for run time {rt} not found at {pred_path}")
            continue

        # Read prediction
        df_pred = pd.read_csv(pred_path)

        if df_pred.empty or df_real.empty:
            print(f"⚠️ Empty dataframe for run time {rt}")
            continue

        # Merge prediction with real data
        merged_df = df_pred.merge(df_real, on="timestamp")  # or whichever common key
        df_merged[rt] = merged_df

        # Plot with Plotly
        fig = px.line(
            merged_df,
            x="Datetime",
            y=["y_pred", "y_real"],
            labels={"value": "MW", "Datetime": "Time", "variable": "Legend"},
            title=f"{region_abbr_caps} - {date_str} - {rt} D0 Run<br>Prediction vs Real"
        )

        fig.update_traces(line=dict(width=2))
        fig.update_layout(
            width=900,
            height=400,
            margin=dict(l=50, r=50, t=60, b=40),
        )

        # Save interactive plot to .json
        plot_path = os.path.join(run_time_folder, f"pred_and_eval_plot_{region_abbr_lwrc}_{rt}.json")
        pio.write_json(fig, plot_path)
        print(f"📈 Interactive plot saved to: {plot_path}")


    

    


