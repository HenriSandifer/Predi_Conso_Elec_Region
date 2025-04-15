from src.plotting.func_plot_pred_only import plot_pred_only
from utils.dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict,
    run_time_dict)
import pandas as pd
import argparse


def run_plotting(region, chosen_day, run_time):
    """
    Plots the full prediction made at any run time

    """
      
    plot_pred_only(
        region,
        region_abbr_caps=region_abbr_caps_dict[region],
        region_abbr_lwrc=region_abbr_dict[region],
        chosen_day=pd.to_datetime(chosen_day),    
        target_month=pd.to_datetime(chosen_day).strftime("%Y-%m"),    
        run_time_str=run_time_dict[run_time],    
        )    
       

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run all models for a given region and prediction time.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")
    parser.add_argument("--time", type=str, required=True, help="Run time (e.g., '02:00:00')")

    args = parser.parse_args()

    run_plotting(args.region, args.day, args.time)   


