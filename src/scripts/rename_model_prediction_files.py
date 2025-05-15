import argparse
from pathlib import Path
import re

def rename_files(region, year, month):
    base_dir = Path(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive")
    region_path = base_dir / region / f"{year}-{month}"
    for date_folder in region_path.iterdir():
        for run_time_folder in date_folder.iterdir():
            if not run_time_folder.exists():
                print(f"⚠️ couldn't find run time folder")
                continue

            for file in run_time_folder.glob("*.csv"):
                old_name = file.name
                match = re.match(r"pred_cons_([a-z]{3})_(.+)_(\d{1,2})D0_(\d{2}-\d{2})_v1_1\.csv", old_name)
                if not match:
                    print(f"⚠️ couldn't find match")
                    continue

                region_abbr, model, hour, date_str = match.groups()
                new_name = f"pred_cons_{region_abbr}_{model}_{hour}_{year}-{date_str}_v1.csv"
                file.rename(run_time_folder / new_name)
                print(f"✅ Renamed {old_name} -> {new_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename local model prediction files.")
    parser.add_argument("--region", type=str, required=True, help="Region code (e.g. ARA, CVL)")
    parser.add_argument("--year", type=str, required=True, help="Year (e.g. 2025)")
    parser.add_argument("--month", type=str, required=True, help="Month (e.g. 02)")
    args = parser.parse_args()
    rename_files(args.region, args.year, args.month)
