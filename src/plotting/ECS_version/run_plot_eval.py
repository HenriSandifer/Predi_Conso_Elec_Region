from src.func_plot_eval import plot_eval
from src.dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict
)

import pandas as pd
from datetime import datetime, timezone, timedelta


def run_plot_eval(region, chosen_day_ymd):
    """
    Plots the prediction made at any run time 
    against the target day's real data

    """
      
    plot_eval(
        region_abbr_caps=region_abbr_caps_dict[region],
        region_abbr_lwrc=region_abbr_dict[region],
        chosen_day=pd.to_datetime(chosen_day_ymd),    
        target_month=pd.to_datetime(chosen_day_ymd).strftime("%Y-%m")    
        )          

def infer_day():
    return (datetime.now(timezone.utc) + timedelta(days=-1, hours=2)).strftime("%Y-%m-%d")

def infer_regions():
    return list(region_abbr_caps_dict.keys())

def infer_month():
    return (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m")


if __name__ == "__main__":
    regions = infer_regions()
    chosen_day_ymd = infer_day()
    chosen_month_ym = infer_month()
    
    print("⚙️ Starting evaluation job...")
    for region in regions:
        run_plot_eval(region, chosen_day_ymd)
