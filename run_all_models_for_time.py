from run_single_prediction import run_pipeline_for_model
from dictionaries import models_by_run_time
from utils import evaluate_all_predictions
from dictionaries import region_abbr_caps_dict, region_abbr_dict, run_time_dict
import pandas as pd
import argparse

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()

    # Assign to the same variable names your script expects
    func_region = args.region
    func_target_day = args.day
    func_run_time = args.time

    models_to_run = models_by_run_time[func_run_time]

    for func_model in models_to_run:
        print(f"⌛ Running {func_model} model...")
        run_pipeline_for_model(
            region=func_region,
            target_day=func_target_day,
            run_time=func_run_time,
            model=func_model
    )

    evaluate_all_predictions(
        region_abbr_caps=region_abbr_caps_dict[func_region],
        region_abbr_lwrc=region_abbr_dict[func_region],
        chosen_day=pd.to_datetime(func_target_day),
        run_time_str=run_time_dict[func_run_time],
        func_region=func_region
    )