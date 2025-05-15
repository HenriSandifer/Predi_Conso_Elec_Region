import os
import pandas as pd
import argparse
from dictionaries import region_abbr_caps_dict, region_abbr_dict

def create_local_full_preds(region, year, month, base_local_dir):
    region_caps = region_abbr_caps_dict[region]
    region_lwrc = region_abbr_dict[region]
    month_path = os.path.join(base_local_dir, region_caps, f"{year}-{month}")

    if not os.path.exists(month_path):
        print(f"❌ Path does not exist: {month_path}")
        return

    for date_folder in os.listdir(month_path):
        date_path = os.path.join(month_path, date_folder)
        if not os.path.isdir(date_path):
            continue

        for run_time_folder in os.listdir(date_path):
            run_time_path = os.path.join(date_path, run_time_folder)
            if not os.path.isdir(run_time_path):
                continue

            all_dfs = []
            for fname in os.listdir(run_time_path):
                if fname.startswith("pred_cons") and fname.endswith(".csv"):
                    fpath = os.path.join(run_time_path, fname)
                    try:
                        df = pd.read_csv(fpath)
                        df.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
                        all_dfs.append(df)
                    except Exception as e:
                        print(f"⚠️ Error reading {fname}: {e}")
                        continue

            if not all_dfs:
                print(f"⚠️ No pred_cons files found for {region_caps} {date_folder} {run_time_folder}")
                continue

            full_df = pd.concat(all_dfs).sort_values("Datetime")
            pred_full_fname = f"pred_full_{region_lwrc}_{date_folder}_{run_time_folder}.csv"
            pred_full_path = os.path.join(run_time_path, pred_full_fname)

            try:
                full_df.to_csv(pred_full_path, index=False)
                print(f"✅ Saved: {pred_full_path}")
            except Exception as e:
                print(f"❌ Failed to write {pred_full_fname}: {e}")

# Example usage
if __name__ == "__main__":
    base_local_dir = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"
    parser = argparse.ArgumentParser(description="Rename local model prediction files.")
    parser.add_argument("--region", type=str, required=True, help="Region full name (e.g. Occitanie)")
    parser.add_argument("--year", type=str, required=True, help="Year (e.g. 2025)")
    parser.add_argument("--month", type=str, required=True, help="Month (e.g. 02)")
    args = parser.parse_args()
    create_local_full_preds(args.region, args.year, args.month, base_local_dir)

