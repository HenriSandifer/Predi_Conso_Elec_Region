import os
import pandas as pd

LOCAL_BASE = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"

def aggregate_monthly_metrics(region_abbr_caps, chosen_month_ym, region_abbr_lwrc):
    """
    Aggregate all evaluation metric CSVs for a region and month into a single CSV file locally.
    Logs missing metric files.
    Only appends new rows.

    """

    month_path = os.path.join(LOCAL_BASE, region_abbr_caps, chosen_month_ym)
    missing_logs = []
    all_metrics = []

    for day_folder in os.listdir(month_path):
        day_path = os.path.join(month_path, day_folder)
        if not os.path.isdir(day_path):
            continue

        for run_time_folder in os.listdir(day_path):
            run_path = os.path.join(day_path, run_time_folder, "eval")
            if not os.path.isdir(run_path):
                continue

            for file in os.listdir(run_path):
                if file.startswith("metrics_individual_models") and file.endswith(".csv"):
                    try:
                        df = pd.read_csv(os.path.join(run_path, file))
                        df["Date"] = day_folder
                        df["Run_time"] = run_time_folder
                        all_metrics.append(df)
                    except Exception as e:
                        print(f"❌ Error reading {file}: {e}")
                        continue
            else:
                # If no metrics file found at all in this eval folder
                metrics_path = os.path.join(run_path, f"metrics_individual_models_{region_abbr_lwrc}_{day_folder}_{run_time_folder}.csv")
                if not os.path.exists(metrics_path):
                    missing_logs.append(metrics_path)

    if not all_metrics:
        print(f"❌ No metrics found for {region_abbr_caps}.")
        return

    # Combine and deduplicate
    new_df = pd.concat(all_metrics, ignore_index=True)
    new_df = new_df[["Date", "Run_time", "Model", "MAE", "RMSE", "R2", "MAE / Mean", "RMSE / Mean"]]

    # Load existing monthly master if it exists
    master_path = os.path.join(month_path, f"metrics_master_{chosen_month_ym}_{region_abbr_lwrc}.csv")
    if os.path.exists(master_path):
        existing_df = pd.read_csv(master_path)
        combined = pd.concat([existing_df, new_df]).drop_duplicates(subset=["Date", "Run_time", "Model"])
    else:
        combined = new_df

    combined.to_csv(master_path, index=False)
    print(f"✅ Monthly master metrics saved to: {master_path}")

    # Save missing log if needed
    if missing_logs:
        log_path = os.path.join(month_path, f"missing_metrics_{chosen_month_ym}_{region_abbr_lwrc}.csv")
        pd.DataFrame({"MissingFile": missing_logs}).to_csv(log_path, index=False)
        print(f"⚠️ Logged missing metric files to: {log_path}")
