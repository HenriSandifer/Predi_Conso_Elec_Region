import pandas as pd
from datetime import datetime, timedelta
import pandas as pd

def get_cons_API_inputs(region: str, chosen_day_input: str, model: str, run_time: str):

    ### Get_consumption_data.py -> uses : region_name, target_day, model, run_time,

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
    
    return {
        "chosen_day": chosen_day,
        "consumption_where": consumption_where,
        "consumption_dates": consumption_dates,
        "Région": Région,
        "run_time": run_time,
        "model": model
    }


