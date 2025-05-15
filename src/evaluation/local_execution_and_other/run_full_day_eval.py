"""
THIS IS FOR A LOCAL RUN / NOT FOR AN S3 RUN
CHANGE FILE BEING IMPORTED FOR S3 RUN
-- in this case, import func_eval_model_pred
-- instead of local_func_eval_model_pred

"""


from local_func_eval_model_pred import evaluate_model_predictions
from src.evaluation.local_execution_and_other.local_func_eval_full_day_pred import evaluate_full_day_prediction
from dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict)

import pandas as pd
import argparse


def run_prediction_evaluation(region, chosen_day):
    """
    Evaluates all predictions (single models + full day)
    for each run_time of a given day once real data is available.

    """

    chosen_day = pd.to_datetime(chosen_day)
    target_month = chosen_day.strftime("%Y-%m")

    region_abbr_caps = region_abbr_caps_dict[region]
    region_abbr_lwrc = region_abbr_dict[region]

    run_times = ["2", "8", "14", "20"]

    for run_time_hr in run_times:
        print(f"🔄 Evaluating predictions for run_time: {run_time_hr}")
        
        try:
            evaluate_model_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr)
        except Exception as e:
            print(f"⚠️ Error evaluating individual model predictions for {run_time_hr}: {e}")

        try:
            evaluate_full_day_prediction(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr)
        except Exception as e:
            print(f"⚠️ Error evaluating full day prediction for {run_time_hr}: {e}")

    print(f"\n✅ Evaluation completed for all run_times on {chosen_day}")      

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")

    args = parser.parse_args()
    run_prediction_evaluation(args.region, args.day)   


