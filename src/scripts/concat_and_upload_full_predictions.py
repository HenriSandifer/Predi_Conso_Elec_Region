import argparse
from pathlib import Path
import pandas as pd
import boto3
from utils_s3 import write_csv_to_s3
from dictionaries import region_abbr_caps_dict, region_abbr_dict

def upload_full_day_preds(region, year, month):
    local_base = Path(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive")
    region_caps = region_abbr_caps_dict[region]
    region_lwrc = region_abbr_dict[region]
    month_path = local_base / region_caps / f"{year}-{month}"
    s3 = boto3.client("s3")

    for date_folder in month_path.iterdir():
        for run_time_folder in date_folder.iterdir():
            pred_path = run_time_folder / "pred"
            if not pred_path.exists():
                continue

            all_dfs = []
            for file in pred_path.glob("pred_cons_*.csv"):
                df = pd.read_csv(file)
                df.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
                all_dfs.append(df)

            if not all_dfs:
                continue

            full_df = pd.concat(all_dfs).sort_values("Datetime")
            run_time_hr = run_time_folder.name
            date_str = date_folder.name
            target_month = f"{year}-{month}"

            s3_key = f"Predictions/{region_caps}/{target_month}/{date_str}/{run_time_hr}/pred/pred_full_{region_lwrc}_{date_str}_{run_time_hr}.csv"
            write_csv_to_s3(full_df, s3_key)
            print(f"📤 Uploaded full day: {s3_key}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate and upload full prediction files to S3.")
    parser.add_argument("--region", type=str, required=True, help="Region code (e.g. ARA, CVL)")
    parser.add_argument("--year", type=str, required=True, help="Year (e.g. 2025)")
    parser.add_argument("--month", type=str, required=True, help="Month (e.g. 02)")
    args = parser.parse_args()
    upload_full_day_preds(args.region, args.year, args.month)
