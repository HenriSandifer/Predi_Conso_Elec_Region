import sys
from datetime import datetime, timedelta, timezone
from src.run_all_models_for_time import run_all_models_for_time
from src.dictionaries import region_abbr_caps_dict

def run_prediction(region, day, run_time_hms):
    try:
        print(f" 🔮 Running prediction for region {region} on {day} at runtime {run_time_hms}...")
        run_all_models_for_time(region, day, run_time_hms)
        print("✅ Prediction successful.")
        return
    except Exception as e:
        print(f"⚠️ Error during prediction: {e}")

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
    print("⚙️ Starting prediction job...")
    print("🧪 sys.argv:", sys.argv)
    
    regions = infer_regions()
    day = infer_day()
    run_time_hms = sys.argv[1] if len(sys.argv) > 1 else infer_run_time()

    for region in regions:
        run_prediction(region, day, run_time_hms)

