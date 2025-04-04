import os
import pandas as pd
from datetime import datetime
import argparse
from dictionaries import region_abbr_caps_dict, region_abbr_dict

def aggregate_all_metrics(region_abbr_caps, region_abbr_lwrc):
    base_dir = os.path.join("Predictions", region_abbr_caps)
    all_metrics = []

    # Loop through each date folder (e.g. 2025-03-01)
    for day_folder in sorted(os.listdir(base_dir)):
        day_path = os.path.join(base_dir, day_folder)
        if not os.path.isdir(day_path):
            continue

        # Loop through each run_time folder (e.g. "2", "8", etc.)
        for run_time in os.listdir(day_path):
            run_time_path = os.path.join(day_path, run_time)
            if not os.path.isdir(run_time_path):
                continue

            metrics_filename = f"evaluation_metrics_{region_abbr_lwrc}_{day_folder}_{run_time}.csv"
            metrics_path = os.path.join(run_time_path, metrics_filename)

            if not os.path.exists(metrics_path):
                print(f"⚠️ Skipping missing file: {metrics_path}")
                continue

            df = pd.read_csv(metrics_path)
            df["Date"] = day_folder
            df["Run_time"] = run_time
            all_metrics.append(df)

    if not all_metrics:
        print(f"❌ No metrics found for region {region_abbr_caps}.")
        return
    
    full_df = pd.concat(all_metrics, ignore_index=True)

    # Reorder columns
    ordered_cols = ["Date", "Run_time", "Model", "MAE", "RMSE", "R2", "MAE / Mean", "RMSE / Mean"]
    full_df = full_df[ordered_cols]

    output_path = os.path.join("Predictions", region_abbr_caps, f"metrics_master_{region_abbr_lwrc}.csv")
    full_df.to_csv(output_path, index=False)
    print(f"✅ Master metrics file saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate all metrics for a given region.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Île-de-France')")
    args = parser.parse_args()

    region_abbr_lwrc = region_abbr_dict[args.region]
    region_abbr_caps = region_abbr_caps_dict[args.region]

    aggregate_all_metrics(region_abbr_caps, region_abbr_lwrc)