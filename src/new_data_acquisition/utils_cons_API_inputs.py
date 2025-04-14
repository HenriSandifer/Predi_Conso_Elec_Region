import pandas as pd
import pandas as pd

def get_cons_API_inputs(region: str, start_dt: pd.Timestamp, end_dt: pd.Timestamp):

    ### Get_consumption_data.py -> uses : region_name, target_day, model, run_time,

    # Generate a list of YYYY-MM-DD strings from start to end
    date_range = pd.date_range(start=start_dt, end=end_dt, freq="D")
    consumption_dates = [dt.strftime("%Y-%m-%d") for dt in date_range]

    # Build API "where" clause
    consumption_where = f'libelle_region:"{region}" AND (' + " OR ".join(
        f'date:\"{d}\"' for d in consumption_dates
    ) + ')'

    # Region
    Région = region
    
    return {
        "consumption_where": consumption_where,
        "consumption_dates": consumption_dates,
        "Région": Région,
    }


