import boto3
import pandas as pd
import io

def aggregate_national_metrics(chosen_month_ym):
    """
    Aggregate all regional monthly metrics into a single national file on S3,
    appending only new rows using Date + Run_time + Model + Region as unique key.

    """
    
    bucket_name = "predi-conso-elec-region"
    s3 = boto3.client("s3")
    prefix = f"Predictions/"
    paginator = s3.get_paginator("list_objects_v2")
    all_metrics = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".csv") and "metrics_master" in key:
                region = key.split("/")[1]
                try:
                    obj_data = s3.get_object(Bucket=bucket_name, Key=key)
                    df = pd.read_csv(io.BytesIO(obj_data["Body"].read()))
                    df["Region"] = region
                    all_metrics.append(df)
                except Exception as e:
                    print(f"❌ Failed to read {key}: {e}")

    if not all_metrics:
        print("❌ No regional monthly metrics found.")
        return

    new_df = pd.concat(all_metrics, ignore_index=True)

    output_key = f"Predictions/metrics_master_national_{chosen_month_ym}.csv"

    # Try to load existing national file
    try:
        existing_obj = s3.get_object(Bucket=bucket_name, Key=output_key)
        existing_df = pd.read_csv(io.BytesIO(existing_obj["Body"].read()))
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        combined.drop_duplicates(subset=["Date", "Run_time", "Model", "Region"], inplace=True)
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            combined = new_df
        else:
            raise

    s3.put_object(Bucket=bucket_name, Key=output_key, Body=combined.to_csv(index=False).encode("utf-8"))
    print(f"✅ National metrics master updated: s3://{bucket_name}/{output_key}")
