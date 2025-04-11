import pandas as pd
from datetime import datetime, timedelta
from utils.dictionaries import (region_abbr_dict,
                                 region_abbr_caps_dict, run_time_dict,
                                   model_delta,
                                     prediction_timeframes)

def get_df_test_inputs(region: str, chosen_day_input: str, model: str, run_time: str):
    
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
        "region_abbr": region_abbr,
        "region_caps": region_abbr_caps,
        "Région": Région,
        "run_time_abbr": run_time_abbr,
        "prediction_timestamps": expected_timestamps,
        "first_row": start_dt,
        "last_row": end_dt,
        "deltatime": deltatime,
        "model": model
    }


