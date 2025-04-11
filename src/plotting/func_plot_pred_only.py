import pandas as pd
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import os
import matplotlib.pyplot as plt

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
    

    # Plot D+1 (Pred only) full-day for run_time
    plt.figure(figsize=(12, 5))
    plt.plot(df_pred_full["Datetime"], df_pred_full["y_pred"], label="Predicted", linewidth=2)
    plt.title(f"{region_abbr_caps} - {chosen_day} - {run_time_str} D0 Run\nPredicted Consumption")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(run_time_folder, f"pred_plot_{region_abbr_lwrc}_{run_time_str}.png")
    plt.savefig(plot_path)
    print(f"📈 Plot saved to: {plot_path}")