from utils.utils import evaluate_all_predictions
from utils.dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict,
    run_time_dict,
)
import pandas as pd
import argparse


def run_prediction_evaluation(func_region, func_target_day, func_run_time):
    """
    Evaluates the full-day prediction after all models have fun.

    """
      
    # Evaluate the full-day concatenated predictions
    evaluate_all_predictions(
        region_abbr_caps=region_abbr_caps_dict[func_region],
        region_abbr_lwrc=region_abbr_dict[func_region],
        chosen_day=pd.to_datetime(func_target_day),    
        target_month=pd.to_datetime(func_target_day).strftime("%Y-%m"),    
        run_time_str=run_time_dict[func_run_time],    
        func_region=func_region    
)            

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()

    run_prediction_evaluation(args.region, args.day, args.time)   


