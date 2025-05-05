from json_func_plot_eval import plot_eval
from dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict
)

import pandas as pd
import argparse


def run_plot_eval(region, chosen_day):
    """
    Plots the prediction made at any run time 
    against the target day's real data

    """
      
    plot_eval(
        region_abbr_caps=region_abbr_caps_dict[region],
        region_abbr_lwrc=region_abbr_dict[region],
        chosen_day=pd.to_datetime(chosen_day),    
        target_month=pd.to_datetime(chosen_day).strftime("%Y-%m")    
        )          

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Plot full-day evaluation comparisons for each run time on a given day.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")

    args = parser.parse_args()

    run_plot_eval(args.region, args.day)   


