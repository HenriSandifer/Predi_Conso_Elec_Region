from src.run_update_cons_data import run_consumption_update
from src.run_update_temperature_forecast import run_temperature_forecast_update

def lambda_handler(event, context):
    """
    Dispatch Lambda function for either temperature or consumption update.
    The `event` must contain a key "task_type" with value "temperature" or "consumption",
    and for temperature updates, also include "run_time" (e.g., "2", "8", etc.).
    
    """

    task_type = event.get("task_type")

    if task_type == "consumption":
        print("⚡ Running electrical consumption update job")
        run_consumption_update()

    elif task_type == "temperature":
        run_time_str = event.get("run_time")
        if not run_time_str:
            raise ValueError("⚠️ Missing 'run_time' for temperature update")
        print(f"🌡️ Running temperature forecast update for run_time = {run_time_str}")
        run_temperature_forecast_update(run_time_str)

    else:
        raise ValueError(f"⚠️ Unknown task_type: {task_type}")