import pandas as pd
from datetime import datetime, timedelta
from utils.dictionaries import (weather_stations, region_abbr_dict,
                                 region_abbr_caps_dict, run_time_dict,
                                   model_delta, holiday_zones,
                                     prediction_timeframes,
                                       models_by_run_time,
                                         lag_roll_features_by_model,
                                           lag_feature_multipliers_by_model,
                                             roll_feature_multipliers)
from vacances_scolaires_france import SchoolHolidayDates
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.metrics import (root_mean_squared_error,
                             mean_absolute_error, r2_score)
import unicodedata

def get_plotting_inputs(region: str, chosen_day_input: str, model: str, run_time: str):


    if isinstance(chosen_day_input, pd.Timestamp):
        chosen_day_str = chosen_day_input.strftime("%Y-%m-%d")
    elif isinstance(chosen_day_input, str):
        chosen_day_str = chosen_day_input
    else:
        raise TypeError("chosen_day must be a string or pandas.Timestamp")

    # Parse chosen day as datetime
    chosen_day = datetime.strptime(chosen_day_str, "%Y-%m-%d")

    # Region
    Région = region
       
    # Build consumption API where clause for the 5 days prior
    num_days = 6
    consumption_dates = [(chosen_day - timedelta(days=i)).strftime("%Y-%m-%d") 
                         for i in range(num_days, 0, -1)]
    
    consumption_where = f'libelle_region:"{region}" AND (' + " OR ".join(
        f'date:"{d}"' for d in consumption_dates
    ) + ')'
    
    # Build consumption API where clause for the past, target, and next day
    num_days = 3
    consumption_dates_2 = [(chosen_day + timedelta(days=i-1)).strftime("%Y-%m-%d") 
                         for i in range(num_days)]
    
    consumption_where_2 = f'libelle_region:"{region}" AND (' + " OR ".join(
        f'date:"{d}"' for d in consumption_dates_2
    ) + ')'

    # For temperature API, target date is 5 days before chosen day
    target_date = (chosen_day - timedelta(days=5)).strftime("%Y-%m-%d")
    
    # Load weather stations from a dictionary file (assumes file "weather_stations.dict" exists)
    stations_for_region = weather_stations.get(region, [])
       
    # Look up the timeframe for the given model/run_time pair
    timeframe = prediction_timeframes.get((model, run_time))
    if timeframe is None:
        raise ValueError(f"No timeframe defined for model {model} at run time {run_time}")
    
    # Build start and end datetime objects using chosen_day's date.
    start_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["start"], "%H:%M:%S").time())
    end_dt = datetime.combine(chosen_day.date(), datetime.strptime(timeframe["end"], "%H:%M:%S").time())

    # Create the expected timestamps for the prediction placeholder
    expected_timestamps = pd.date_range(start=start_dt, end=end_dt, freq="15min")

    #Gets 
    delta = model_delta.get(model)

    deltatime = timedelta(hours=delta)

    # Dictionary for region abbreviations
    region_abbr = region_abbr_dict.get(region, "NA")

   #Dictionary for capitalized region abbreviations
    region_abbr_caps = region_abbr_caps_dict.get(region, "NA")

    #Dictionary for run_time abbreviations
    run_time_abbr = run_time_dict.get(run_time, "NA")
   
    return {
        "chosen_day": chosen_day,
        "consumption_where": consumption_where,
        "consumption_dates": consumption_dates,
        "target_date": target_date,
        "stations_for_region": stations_for_region,
        "region_abbr": region_abbr,
        "region_caps": region_abbr_caps,
        "Région": Région,
        "consumption_where_2": consumption_where_2,
        "consumption_dates_2": consumption_dates_2,
        "model_antic": delta,
        "run_time": run_time,
        "run_time_abbr": run_time_abbr,
        "prediction_timestamps": expected_timestamps,
        "first_row": start_dt,
        "last_row": end_dt,
        "deltatime": deltatime,
        "func_model": model
    }


