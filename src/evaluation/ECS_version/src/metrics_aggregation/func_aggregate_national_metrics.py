import boto3
import pandas as pd
import io

def aggregate_national_metrics(chosen_month_ym):
    """
    Aggregate all regional monthly metrics into a single national file.
    
    """
    bucket_name="predi-conso-elec-region"
    s3 = boto3.client("s3")
    prefix = f"Predictions/"
    paginator = s3.get_paginator("list_objects_v2")
    all_metrics = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(f"metrics_master_{chosen_month_ym}.csv"):
                region = key.split("/")[1]
                obj_data = s3.get_object(Bucket=bucket_name, Key=key)
                df = pd.read_csv(io.BytesIO(obj_data["Body"].read()))
                df["Region"] = region
                all_metrics.append(df)

    if not all_metrics:
        print("❌ No regional metrics found.")
        return

    national_df = pd.concat(all_metrics, ignore_index=True)

    # Save to S3
    output_key = f"Predictions/metrics_master_national_{chosen_month_ym}.csv"
    s3.put_object(Bucket=bucket_name, Key=output_key, Body=national_df.to_csv(index=False).encode("utf-8"))
    print(f"✅ National master metrics saved to: s3://{bucket_name}/{output_key}")
