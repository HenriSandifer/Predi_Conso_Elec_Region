import pandas as pd
from utils_s3 import read_csv_from_s3, write_csv_to_s3
import boto3
from datetime import datetime, timezone, timedelta

# Set up S3 client
s3 = boto3.client('s3')

# Your bucket and file paths
BUCKET_NAME = "predi-conso-elec-region"
SOURCE_KEY = "raw_data/real_cons_data.csv"

# Step 0: Create a backup
def backup_s3_file(bucket_name, source_key):
    timestamp = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m-%d_%H-%M-%S")
    backup_key = f"raw_data/real_cons_data_backup_{timestamp}.csv"

    print(f"🛡️ Creating backup at s3://{bucket_name}/{backup_key}")
    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': source_key},
        Key=backup_key
    )
    print("✅ Backup created.")

# Step 1: Read existing data
df = read_csv_from_s3(SOURCE_KEY)

if df is not None and not df.empty:
    print("📥 Successfully loaded data from S3.")

    # Step 0 (continued): Backup before doing anything else
    backup_s3_file(BUCKET_NAME, SOURCE_KEY)

    # Step 2: Preprocess Datetime column
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df.sort_values(["Région", "Datetime"], inplace=True)

    # Step 3: Resample and interpolate for each region separately
    resampled_dfs = []

    for region, group in df.groupby("Région"):
        group = group.set_index("Datetime")

        # Resample at 15-minute intervals
        group_resampled = group.resample("15T").asfreq()

        # Forward-fill the region name
        group_resampled["Région"] = region

        # Interpolate "Consommation (MW)" values
        group_resampled["Consommation (MW)"] = (
            group_resampled["Consommation (MW)"]
            .infer_objects(copy=False)
            .interpolate(method="linear")
        )

        resampled_dfs.append(group_resampled.reset_index())

    # Step 4: Concatenate all regions back together
    df_resampled = pd.concat(resampled_dfs).sort_values(["Datetime", "Région"])

    # Step 5: Save back to original S3 path
    write_csv_to_s3(df_resampled, SOURCE_KEY)
    print("✅ Resampled and interpolated data saved to S3.")

else:
    print("⚠️ No data loaded from S3. Exiting.")
