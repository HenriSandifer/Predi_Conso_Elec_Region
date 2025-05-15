from src.evaluation.func_eval_model_pred import evaluate_model_predictions
from src.evaluation.func_eval_full_day_pred import evaluate_full_day_prediction
from src.utils.dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict)

import pandas as pd


def run_full_day_prediction_evaluation(region, chosen_day_ymd):
    """
    Evaluates all predictions (single models + full day)
    for each run_time of a given day once real data is available.

    """

    chosen_day_ymd = pd.to_datetime(chosen_day_ymd)
    target_month = chosen_day_ymd.strftime("%Y-%m")

    region_abbr_caps = region_abbr_caps_dict[region]
    region_abbr_lwrc = region_abbr_dict[region]

    run_times = ["2", "8", "14", "20"]

    for run_time_hr in run_times:
        print(f"🔄 Evaluating predictions for run_time: {run_time_hr}")
        
        try:
            evaluate_model_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day_ymd, run_time_hr)
        except Exception as e:
            print(f"⚠️ Error evaluating individual model predictions for {run_time_hr}: {e}")

        try:
            evaluate_full_day_prediction(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day_ymd, run_time_hr)
        except Exception as e:
            print(f"⚠️ Error evaluating full day prediction for {run_time_hr}: {e}")

    print(f"\n✅ Evaluation completed for all run_times on {chosen_day_ymd}")