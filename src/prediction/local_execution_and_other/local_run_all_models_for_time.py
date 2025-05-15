import os
import pandas as pd
import argparse
from local_func_single_prediction import run_pipeline_for_model
from dictionaries import (
    models_by_run_time,
    region_abbr_caps_dict,
    run_time_dict,
    region_abbr_dict,
)


def run_all_models_for_time(region, chosen_day, run_time_hms):
    """
    Runs all models for a given region, target day, and run time.
    Concatenates all predictions into a full-day CSV stored locally.
    """

    region_abbr_caps = region_abbr_caps_dict.get(region, "NA")
    target_month = pd.to_datetime(chosen_day).strftime("%Y-%m")
    run_time_hr = run_time_dict.get(run_time_hms, "NA")
    region_abbr_lwrc = region_abbr_dict.get(region, "NA")

    models_to_run = models_by_run_time[run_time_hms]

    for model in models_to_run:
        print(f"⌛ Running {model} model...")
        run_pipeline_for_model(region, chosen_day, run_time_hms, model)

    # Build path to where model predictions were saved locally
    date_str = pd.to_datetime(chosen_day).strftime("%Y-%m-%d")
    local_base = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"
    run_time_path = os.path.join(
        local_base,
        region_abbr_caps,
        target_month,
        date_str,
        str(run_time_hr),
        "pred"
    )

    if not os.path.exists(run_time_path):
        print(f"❌ Folder not found: {run_time_path}")
        return

    pred_files = [
        f for f in os.listdir(run_time_path)
        if f.startswith("pred_cons_") and f.endswith(".csv")
    ]

    if not pred_files:
        print(f"⚠️ No pred_cons CSVs found in {run_time_path}")
        return

    full_day_df = []
    for fname in pred_files:
        fpath = os.path.join(run_time_path, fname)
        df = pd.read_csv(fpath)
        df.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        full_day_df.append(df)

    df_pred_full = pd.concat(full_day_df).sort_values("Datetime")

    pred_filename = f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    local_path = os.path.join(run_time_path, pred_filename)

    df_pred_full.to_csv(local_path, index=False)
    print(f"✅ Saved full-day prediction to: {local_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Chosen day (e.g., '2025-03-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()
    run_all_models_for_time(args.region, args.day, args.time)
