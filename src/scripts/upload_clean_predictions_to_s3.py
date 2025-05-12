import os
import pandas as pd
from utils_s3 import write_csv_to_s3

def clean_and_upload_predictions(region_abbr_caps, year, month, base_local_dir):

    region_abbr_lwrc = region_abbr_caps.lower()
    month_str = f"{year}-{month:02d}"
    region_local_path = os.path.join(base_local_dir, region_abbr_caps, month_str)

    if not os.path.exists(region_local_path):
        print(f"❌ Local path does not exist: {region_local_path}")
        return

    for day_folder in os.listdir(region_local_path):
        day_path = os.path.join(region_local_path, day_folder)

        if not os.path.isdir(day_path):
            continue

        for run_time in os.listdir(day_path):
            run_path = os.path.join(day_path, run_time)
            if not os.path.isdir(run_path):
                continue

            for fname in os.listdir(run_path):
                fpath = os.path.join(run_path, fname)

                if not fname.endswith(".csv"):
                    continue

                if fname.startswith("pred_cons"):
                    # Example: pred_cons_ara_M36_2D0_02-01_v1_1.csv
                    # → pred_cons_ara_M36_2_02-01_v1.csv
                    parts = fname.split("_")
                    if len(parts) < 6:
                        print(f"⚠️ Unexpected filename: {fname}")
                        continue

                    # Clean run_time
                    run_time_raw = parts[4]  # e.g., "2D0"
                    run_time_clean = ''.join([c for c in run_time_raw if c.isdigit()])

                    # Clean version
                    version_section = parts[-1]  # e.g., "v1_1.csv"
                    version_clean = version_section.split(".")[0].split("_")[0]  # keep "v1"

                    new_fname = "_".join(parts[:4] + [run_time_clean, parts[5], version_clean]) + ".csv"
                    s3_key = f"Predictions/{region_abbr_caps}/{month_str}/{day_folder}/{run_time}/pred/{new_fname}"

                elif fname.startswith("evaluation_metrics"):
                    # → metrics_individual_models_ara_2025-02-01_2.csv
                    parts = fname.split("_")
                    if len(parts) < 5:
                        print(f"⚠️ Unexpected metrics filename: {fname}")
                        continue

                    date_str = parts[3]
                    run_time_hr = parts[4].replace(".csv", "")
                    new_fname = f"metrics_individual_models_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
                    s3_key = f"Predictions/{region_abbr_caps}/{month_str}/{day_folder}/{run_time}/eval/{new_fname}"

                else:
                    print(f"⚠️ Skipping unrecognized file: {fname}")
                    continue

                try:
                    df = pd.read_csv(fpath)
                    write_csv_to_s3(df, s3_key)
                except Exception as e:
                    print(f"❌ Error uploading {fname}: {e}")
