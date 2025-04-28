import pandas as pd
import boto3
import io

def aggregate_monthly_metrics(region_abbr_caps, chosen_month_ym, region_abbr_lwrc):
    """
    Aggregate all evaluation metric CSVs for a region and month into a single CSV file on S3.
    
    """
    bucket_name="predi-conso-elec-region"
    s3 = boto3.client("s3")
    prefix = f"Predictions/{region_abbr_caps}/{chosen_month_ym}/"
    paginator = s3.get_paginator("list_objects_v2")
    all_metrics = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".csv") and "evaluation_metrics" in key:
                obj_data = s3.get_object(Bucket=bucket_name, Key=key)
                df = pd.read_csv(io.BytesIO(obj_data["Body"].read()))

                # Extract day and runtime from filename
                parts = key.split("/")
                day = parts[3]  # "2025-04-10"
                run_time = parts[4]  # "2"

                df["Date"] = day
                df["Run_time"] = run_time
                all_metrics.append(df)

    if not all_metrics:
        print(f"❌ No metrics found for region {region_abbr_caps}.")
        return

    full_df = pd.concat(all_metrics, ignore_index=True)

    # Reorder columns
    ordered_cols = ["Date", "Run_time", "Model", "MAE", "RMSE", "R2", "MAE / Mean", "RMSE / Mean"]
    full_df = full_df[ordered_cols]

    output_key = f"Predictions/{region_abbr_caps}/{chosen_month_ym}/metrics_master_{chosen_month_ym}_{region_abbr_lwrc}.csv"
    s3.put_object(Bucket=bucket_name, Key=output_key, Body=full_df.to_csv(index=False).encode("utf-8"))
    print(f"✅ Master metrics file saved to: s3://{bucket_name}/{output_key}")
