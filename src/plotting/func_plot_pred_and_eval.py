import pandas as pd
from utils.dictionaries import (weather_stations, region_abbr_dict,
                                 region_abbr_caps_dict, run_time_dict,
                                   model_delta, holiday_zones,
                                     prediction_timeframes,
                                       models_by_run_time,
                                         lag_roll_features_by_model,
                                           lag_feature_multipliers_by_model,
                                             roll_feature_multipliers)
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import (root_mean_squared_error,
                             mean_absolute_error, r2_score)
import unicodedata

def plot_pred_and_eval(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str):
    
    """
    Generate plot for D-1 Prediction + Evaluation
    
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


    for rt, df in df_merged.items():
        plot_df_vs_real(df, run_time=rt)

        
    # Plot D-1 (Pred + Real)
    plt.figure(figsize=(12, 5))
    plt.plot(df_merged[rt]["Datetime"], df_merged[rt]["y_real"], label="Real", linewidth=2)
    plt.plot(df_merged[rt]["Datetime"], df_merged[rt]["y_pred"], label="Predicted", linestyle="--")
    plt.title(f"{region_abbr_caps} - {chosen_day} - {run_time_str} D0 Run\nPredicted vs Real Consumption")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(run_time_folder, f"pred_&_eval_plot_{region_abbr_lwrc}_{run_time_str}.png")
    plt.savefig(plot_path)
    print(f"📈 Plot saved to: {plot_path}")

    

    


