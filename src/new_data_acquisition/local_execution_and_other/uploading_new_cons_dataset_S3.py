import pandas as pd
from utils_s3 import write_csv_to_s3
import boto3
from datetime import datetime, timezone, timedelta

# Set up S3 client
s3 = boto3.client('s3')

# Your bucket and file paths
BUCKET_NAME = "predi-conso-elec-region"
SOURCE_KEY = "raw_data/real_cons_data.csv"
LOCAL_FILE_PATH = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\reg_2025_cons_new.csv"

# Step 0: Create a backup of the current S3 file
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

# Step 1: Backup the existing real_cons_data
backup_s3_file(BUCKET_NAME, SOURCE_KEY)

# Step 2: Load your new local dataset
print(f"📄 Loading new dataset from {LOCAL_FILE_PATH}")
df = pd.read_csv(LOCAL_FILE_PATH)

# Step 3: Preprocess Datetime column
df["Datetime"] = pd.to_datetime(df["Datetime"])
df.sort_values(["Région", "Datetime"], inplace=True)

# Step 4: Resample and interpolate for each region separately
resampled_dfs = []

for region, group in df.groupby("Région"):

    # Remove duplicate timestamps inside the Region group
    group = group.drop_duplicates(subset=["Datetime"], keep='first')
    
    group = group.set_index("Datetime")

    # Resample at 15-minute intervals
    group_resampled = group.resample("15min").asfreq()

    # Forward-fill the region name
    group_resampled["Région"] = region

    # Interpolate "Consommation (MW)" values
    group_resampled["Consommation (MW)"] = (
        group_resampled["Consommation (MW)"]
        .infer_objects(copy=False)
        .interpolate(method="linear")
    )

    resampled_dfs.append(group_resampled.reset_index())   

# Step 5: Concatenate all regions back together
df_resampled = pd.concat(resampled_dfs).sort_values(["Datetime", "Région"])

# Step 6: Upload the cleaned data to S3
write_csv_to_s3(df_resampled, SOURCE_KEY)
print("✅ New resampled and interpolated data saved to S3.")

