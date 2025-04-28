from func_eval_model_pred import evaluate_model_predictions
from func_eval_full_day_pred import evaluate_full_day_prediction
from dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict,
    run_time_dict
)

import pandas as pd
import argparse


def run_single_runtime_evaluation(region, chosen_day_str, run_time_hms):
    """
    Evaluates model predictions and full-day prediction
    for a given region, day, and run_time.
    """

    chosen_day = pd.to_datetime(chosen_day_str)
    target_month = chosen_day.strftime("%Y-%m")

    region_abbr_caps = region_abbr_caps_dict[region]
    region_abbr_lwrc = region_abbr_dict[region]

    run_time_hr = run_time_dict.get(run_time_hms)

    print(f"🔄 Evaluating predictions for run_time: {run_time_hr}")

    try:
        evaluate_model_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr)
        print(f"\n✅ Evaluation completed for individual models on {chosen_day_str} at run_time {run_time_hr} in {region}")
    except Exception as e:
        print(f"⚠️ Error evaluating individual model predictions for run_time {run_time_hr}: {e}")

    try:
        evaluate_full_day_prediction(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr)
        print(f"\n✅ Evaluation completed for full day on {chosen_day_str} at run_time {run_time_hr} in {region}")
    except Exception as e:
        print(f"⚠️ Error evaluating full day prediction for run_time {run_time_hr}: {e}")

    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluate model predictions for a given region, day, and run_time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-04-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '2')")

    args = parser.parse_args()

    run_single_runtime_evaluation(args.region, args.day, args.time)
