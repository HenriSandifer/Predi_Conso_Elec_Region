import sys
import time
from datetime import datetime
print(f"🛠️ Runtime argument passed: {sys.argv}")
from src.run_update_cons_data import run_consumption_update
from src.run_update_temperature_forecast import run_temperature_forecast_update

def run_all(run_time_pstr, max_retries=3, delay=300):
    for attempt in range(1, max_retries + 1):
        try:
            print(f"⚡ Attempt {attempt} to update data...")
            run_consumption_update()
            run_temperature_forecast_update(run_time_pstr)
            print("✅ Data update successful.")
            return
        except Exception as e:
            print(f"⚠️ Error during update: {e}")
            if attempt < max_retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Max retries reached. Exiting with failure.")
                sys.exit(1)

def infer_run_time():
    hour = datetime.now(datetime.timezone.utc+2).hour
    if hour < 6:
        return "02"
    elif hour < 12:
        return "08"
    elif hour < 18:
        return "14"
    else:
        return "20"

if __name__ == "__main__":
    print("⚡ Starting data update job...")

    run_time_pstr = sys.argv[1] if len(sys.argv) > 1 else infer_run_time()
    run_all(run_time_pstr)

