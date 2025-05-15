import os
import pandas as pd

LOCAL_BASE = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"

def aggregate_national_metrics(target_month="2025-04"):
    """
    Aggregate all regional monthly metrics into a national file.
    Only appends unseen rows.
    """

    all_metrics = []
    region_dirs = [d for d in os.listdir(LOCAL_BASE) if os.path.isdir(os.path.join(LOCAL_BASE, d))]

    for region_abbr_caps in region_dirs:
        region_path = os.path.join(LOCAL_BASE, region_abbr_caps, target_month)
        master_filename = f"metrics_master_{target_month}_{region_abbr_caps.lower()}.csv"
        master_path = os.path.join(region_path, master_filename)

        if not os.path.exists(master_path):
            print(f"⚠️ Missing regional master: {master_path}")
            continue

        try:
            df = pd.read_csv(master_path)
            df["Region"] = region_abbr_caps
            all_metrics.append(df)
        except Exception as e:
            print(f"❌ Error reading {master_path}: {e}")

    if not all_metrics:
        print("❌ No regional master metrics found.")
        return

    national_df = pd.concat(all_metrics, ignore_index=True)

    # Save or append to national file
    national_path = os.path.join(LOCAL_BASE, f"metrics_master_national_{target_month}.csv")

    if os.path.exists(national_path):
        existing_df = pd.read_csv(national_path)
        combined = pd.concat([existing_df, national_df]).drop_duplicates(subset=["Date", "Run_time", "Model", "Region"])
    else:
        combined = national_df

    combined.to_csv(national_path, index=False)
    print(f"✅ National metrics master saved to: {national_path}")
