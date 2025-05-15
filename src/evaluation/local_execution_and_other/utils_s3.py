import os
import boto3
import pandas as pd
from io import StringIO
from datetime import datetime

# Get your bucket name from an environment variable (or default to correct S3 bucket)
S3_BUCKET = os.getenv("MY_PROJECT_BUCKET", "predi-conso-elec-region")

# Initialize S3 client (you can add region_name or credentials if needed)
s3 = boto3.client("s3")

def read_csv_from_s3(key):

    """
    Reads a CSV file from the S3 bucket using the specified key (path in bucket)
    
    """
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(response["Body"])
    except Exception as e:
        print(f"❌ Error reading from S3: s3://{S3_BUCKET}/{key}\n{e}")
        return None

def write_csv_to_s3(df, key):

    """
    Writes a DataFrame to S3 as a CSV using the specified key (path in bucket)
    
    """
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=csv_buffer.getvalue())
        print(f"✅ File written to: s3://{S3_BUCKET}/{key}")
    except Exception as e:
        print(f"❌ Error writing to S3: s3://{S3_BUCKET}/{key}\n{e}")

def get_last_fully_predicted_date(region_abbr_caps, target_month):

    """
    Returns the last date (datetime.date) for which all 4 run_times (2,8,14,20) have prediction files.
    
    """
    base_dir = "Predictions"
    prefix = f"{base_dir}/{region_abbr_caps}/{target_month}/"

    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

        date_run_map = {}

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                parts = key.split("/")

                if len(parts) >= 6:
                    _, region, month, date_str, run_time, *_ = parts
                    if date_str not in date_run_map:
                        date_run_map[date_str] = set()
                    date_run_map[date_str].add(run_time)

        valid_dates = [
            datetime.strptime(d, "%Y-%m-%d").date()
            for d, times in date_run_map.items()
            if {"2", "8", "14", "20"}.issubset(times)
        ]

        return max(valid_dates) if valid_dates else None

    except Exception as e:
        print(f"❌ Error checking S3 for latest predictions:\n{e}")
        return None

def get_last_fully_evaluated_date(region_abbr_caps, target_month):

    """
    Returns the last date (datetime.date) for which all 4 run_times (2,8,14,20) have prediction files.
    
    """
    base_dir = "Predictions"
    prefix = f"{base_dir}/{region_abbr_caps}/{target_month}/"

    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

        date_run_map = {}

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                parts = key.split("/")

                if len(parts) >= 6:
                    _, region, month, date_str, run_time, *_ = parts
                    if date_str not in date_run_map:
                        date_run_map[date_str] = set()
                    date_run_map[date_str].add(run_time)

        valid_dates = [
            datetime.strptime(d, "%Y-%m-%d").date()
            for d, times in date_run_map.items()
            if {"2", "8", "14", "20"}.issubset(times)
        ]

        return max(valid_dates) if valid_dates else None

    except Exception as e:
        print(f"❌ Error checking S3 for latest predictions:\n{e}")
        return None

