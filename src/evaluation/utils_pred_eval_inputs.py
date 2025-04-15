import pandas as pd
from datetime import datetime
from utils.dictionaries import prediction_timeframes
import pandas as pd

def get_pred_eval_inputs(region: str, chosen_day_input: str, model: str, run_time: str):
       
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
   
    return {
        "chosen_day": chosen_day,
        "Région": Région,
        "run_time": run_time,
        "first_row": start_dt,
        "last_row": end_dt
    }


