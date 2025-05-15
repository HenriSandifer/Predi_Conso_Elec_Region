import argparse
import os
import boto3
import pandas as pd
from dictionaries import region_abbr_caps_dict
from utils_s3 import write_csv_to_s3

def upload_selected_predictions(region, year, month, base_local_dir):
    region_caps = region_abbr_caps_dict[region]
    month_str = f"{year}-{month}"
    local_month_path = os.path.join(base_local_dir, region_caps, month_str)

    if not os.path.exists(local_month_path):
        print(f"❌ Path does not exist: {local_month_path}")
        return

    s3 = boto3.client("s3")
    bucket_name = "predi-conso-elec-region"

    for day_folder in os.listdir(local_month_path):
        day_path = os.path.join(local_month_path, day_folder)
        if not os.path.isdir(day_path):
            continue

        for run_time in os.listdir(day_path):
            run_path = os.path.join(day_path, run_time)
            if not os.path.isdir(run_path):
                continue

            for fname in os.listdir(run_path):
                if not fname.endswith(".csv"):
                    continue
                if not (fname.startswith("pred_cons") or fname.startswith("pred_full")):
                    continue

                local_file_path = os.path.join(run_path, fname)
                s3_key = f"Predictions/{region_caps}/{month_str}/{day_folder}/{run_time}/pred/{fname}"

                try:
                    df = pd.read_csv(local_file_path)
                    write_csv_to_s3(df, s3_key)
                    print(f"📤 Uploaded {fname} to s3://{bucket_name}/{s3_key}")
                except Exception as e:
                    print(f"❌ Failed to upload {fname}: {e}")

if __name__ == "__main__":
    base_local_dir = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"
    parser = argparse.ArgumentParser(description="Upload selected prediction files to S3.")
    parser.add_argument("--region", type=str, required=True, help="Region full name (e.g. Occitanie")
    parser.add_argument("--year", type=str, required=True, help="Year (e.g. 2025)")
    parser.add_argument("--month", type=str, required=True, help="Month (e.g. 02)")
    args = parser.parse_args()
    upload_selected_predictions(
        region=args.region,
        year=args.year,
        month=args.month,
        base_local_dir=base_local_dir
    )
