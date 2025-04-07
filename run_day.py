from run_all_models_for_time import run_all_models_for_time
from dictionaries import run_time_dict
import argparse


def run_all_for_day(func_region, func_target_day):
    
    # === Loop through run times ===
    for run_time in run_time_dict:
        print(f"🚀 Running predictions for {func_region} on {func_target_day} at {run_time}")
        run_all_models_for_time(func_region, func_target_day, run_time)

    print(f"☑️ Finished full day prediction for {func_target_day} in {func_region}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all predictions for a given region and a given day.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--day", type=str, required=True, help="Target day (e.g., '2025-03-10')")

    args = parser.parse_args()
    run_all_for_day(args.region, args.day)