import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

def plot_pred_only(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    
    """
    Generate plot for D+1 Prediction
    
    """
        
    date_str = chosen_day.strftime("%Y-%m-%d")
    base_dir = "Predictions"
    run_time_folder = os.path.join(base_dir, region_abbr_caps, str(target_month), date_str, str(run_time_str))

    # Gather CSV files
    prediction_files = [
        os.path.join(run_time_folder, f)
        for f in os.listdir(run_time_folder)
        if f.endswith(".csv") and "all_models" not in f  # Avoid reloading concatenated full-day prediction
    ]

    if not prediction_files:
        print("⚠️ No prediction files found for this run time.")
        return

    
    # File Read    
    pred_path = os.path.join(run_time_folder, f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_str}.csv")
    df_pred_full = pd.read_csv(pred_path, parse_dates="Datetime") 
    

    # Plot using Plotly
    fig = px.line(
        df_pred_full,
        x="Datetime",
        y="y_pred",
        title=f"{region_abbr_caps} - {chosen_day.strftime('%Y-%m-%d')} - {run_time_str} D0 Run<br>Predicted Consumption (MW)",
        labels={"Datetime": "Time", "y_pred": "Predicted Consumption (MW)"}
    )

    fig.update_layout(
        width=900,
        height=400,
        margin=dict(l=50, r=50, t=60, b=40),
    )

    # Save to interactive .json format
    plot_path = os.path.join(run_time_folder, f"pred_plot_{region_abbr_lwrc}_{run_time_str}.json")
    pio.write_json(fig, plot_path)
    print(f"📈 Interactive plot saved to: {plot_path}")