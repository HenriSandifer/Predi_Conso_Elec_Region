from src.prediction.func_single_prediction import run_pipeline_for_model
from utils.dictionaries import models_by_run_time
import pandas as pd
import argparse
import os

def run_all_models_for_time(region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_str, region, run_time):
    """
    Runs all models for a given region, target day, and run time.

    Saves CSV of concatenated prediction for run_time

    """
    models_to_run = models_by_run_time[run_time]

    for model in models_to_run:
        print(f"⌛ Running {model} model...")
        run_pipeline_for_model(region, chosen_day, run_time, model)
    
    ### Saving full day prediction of given run_time

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

    full_day_df = []

    for file in prediction_files:
        df_pred = pd.read_csv(file, parse_dates=["Datetime"])
                
        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        
        full_day_df.append(df_pred)

    # Full day concatenation
    df_pred_full = pd.concat(full_day_df).sort_values("Datetime")

    # Save df_pred_full to CSV for later evaluation and plotting
    pred_path = os.path.join(run_time_folder, f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_str}.csv")
    df_pred_full.to_csv(pred_path, index=False)

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Chosen day (e.g., '2025-03-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()

    run_all_models_for_time(args.region, args.day, args.time)   