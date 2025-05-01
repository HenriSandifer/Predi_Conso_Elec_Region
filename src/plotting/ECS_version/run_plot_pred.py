from src.func_plot_pred import plot_pred
from src.dictionaries import (
    region_abbr_caps_dict,
    region_abbr_dict,
    run_time_dict)
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys

def run_plot_pred(region, chosen_day_ymd, run_time_hms):
    """
    Plots the full prediction made at a specific run_time

    """
      
    plot_pred(
        region_abbr_caps=region_abbr_caps_dict[region],
        region_abbr_lwrc=region_abbr_dict[region],
        chosen_day=pd.to_datetime(chosen_day_ymd),    
        target_month=pd.to_datetime(chosen_day_ymd).strftime("%Y-%m"),    
        run_time_hr=run_time_dict[run_time_hms],    
        )    
       
def infer_run_time():
    now = datetime.now(timezone.utc) + timedelta(hours=2)
    hour = now.hour
    if hour < 6:
        return "02:00:00"
    elif hour < 12:
        return "08:00:00"
    elif hour < 18:
        return "14:00:00"
    else:
        return "20:00:00"
    
def infer_day():
    return (datetime.now(timezone.utc) + timedelta(days=1, hours=2)).strftime("%Y-%m-%d")

def infer_regions():
    return list(region_abbr_caps_dict.keys())


if __name__ == "__main__":

    print("⚡ Starting data update job...")

    regions = infer_regions()
    chosen_day_ymd = infer_day()
    run_time_hms = sys.argv[1] if len(sys.argv) > 1 else infer_run_time()

    for region in regions:
        run_plot_pred(region, chosen_day_ymd, run_time_hms)


