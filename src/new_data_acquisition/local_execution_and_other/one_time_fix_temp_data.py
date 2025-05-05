from utils_s3 import read_csv_from_s3, write_csv_to_s3
import pandas as pd
import boto3
from datetime import datetime, timezone, timedelta

# Set up S3 client
s3 = boto3.client('s3')

# Your bucket and file paths
BUCKET_NAME = "predi-conso-elec-region"
SOURCE_KEY = "raw_data/temperature_forecast_data.csv"

# Step 0: Create a backup
def backup_s3_file(bucket_name, source_key):
    timestamp = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m-%d_%H-%M-%S")
    backup_key = f"raw_data/temperature_forecast_data_backup_{timestamp}.csv"

    print(f"🛡️ Creating backup at s3://{bucket_name}/{backup_key}")
    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': source_key},
        Key=backup_key
    )
    print("✅ Backup created.")

# Backup before doing anything else
backup_s3_file(BUCKET_NAME, SOURCE_KEY)

# Define the columns to keep
columns_to_keep = ['Datetime', 'Région', 'hist_t', 'temp_02', 'temp_08', 'temp_20', 'temp_14']

# Step 1: Load the existing data
df_existing = read_csv_from_s3(SOURCE_KEY)

if df_existing is not None:
    # Step 2: Filter the columns
    df_cleaned = df_existing[columns_to_keep]

    # Step 3: Save the cleaned version back to S3
    write_csv_to_s3(df_cleaned, SOURCE_KEY)
