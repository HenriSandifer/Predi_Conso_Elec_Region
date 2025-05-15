import pandas as pd
import boto3
import io

def aggregate_monthly_metrics(region_abbr_caps, chosen_month_ym, region_abbr_lwrc):
    """
    Aggregate all evaluation metric CSVs for a region and month into a single CSV file on S3,
    appending only new rows (no overwrite), using Date + Run_time + Model as unique ID.

    """
    
    bucket_name = "predi-conso-elec-region"
    s3 = boto3.client("s3")
    prefix = f"Predictions/{region_abbr_caps}/{chosen_month_ym}/"
    paginator = s3.get_paginator("list_objects_v2")
    all_metrics = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        print(f"page is : {page}")
        for obj in page.get("Contents", []):
            print(f"obj is : {obj}")
            key = obj["Key"]
            print(f"key is : {key}")
            if key.endswith(".csv") and "/eval/" in key and "metrics" in key:
                try:
                    obj_data = s3.get_object(Bucket=bucket_name, Key=key)
                    df = pd.read_csv(io.BytesIO(obj_data["Body"].read()))
                    parts = key.split("/")
                    print(f"len parts is : {len(parts)}")
                    print(f"parts[-1] is : {parts[-1]}")
                    print(f"parts[0] is : {parts[0]}")
                    print(f"parts[1] is : {parts[1]}")
                    print(f"parts[2] is : {parts[2]}")
                    print(f"parts[3] is : {parts[3]}")
                    print(f"parts[4] is : {parts[4]}")
                    print(f"parts[5] is : {parts[5]}")
                    print(f"parts[6] is : {parts[6]}")
                    if len(parts) >= 6:
                        day = parts[3]
                        run_time = parts[4]
                        df["Date"] = day
                        df["Run_time"] = run_time
                        all_metrics.append(df)
                except Exception as e:
                    print(f"❌ Failed to read {key}: {e}")

    if not all_metrics:
        print(f"❌ No metrics found for region {region_abbr_caps}.")
        return

    new_df = pd.concat(all_metrics, ignore_index=True)
    new_df = new_df[["Date", "Run_time", "Model", "MAE", "RMSE", "R2", "MAE / Mean", "RMSE / Mean"]]

    # Load existing master if it exists
    output_key = f"Predictions/{region_abbr_caps}/{chosen_month_ym}/metrics_master_{chosen_month_ym}_{region_abbr_lwrc}.csv"
    try:
        existing_obj = s3.get_object(Bucket=bucket_name, Key=output_key)
        existing_df = pd.read_csv(io.BytesIO(existing_obj["Body"].read()))
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        combined.drop_duplicates(subset=["Date", "Run_time", "Model"], inplace=True)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            combined = new_df
        else:
            raise

    s3.put_object(Bucket=bucket_name, Key=output_key, Body=combined.to_csv(index=False).encode("utf-8"))
    print(f"✅ Monthly metrics master updated: s3://{bucket_name}/{output_key}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test monthly metrics aggregation on S3.")
    parser.add_argument("--region_abbr_caps", type=str, required=True, help="Region abbreviation in CAPS, e.g. 'BFC'")
    parser.add_argument("--region_abbr_lwrc", type=str, required=True, help="Region abbreviation in lowercase, e.g. 'bfc'")
    parser.add_argument("--month", type=str, required=True, help="Month in YYYY-MM format, e.g. '2025-05'")

    args = parser.parse_args()
    aggregate_monthly_metrics(args.region_abbr_caps, args.month, args.region_abbr_lwrc)
