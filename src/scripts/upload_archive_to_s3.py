import os
import boto3
from pathlib import Path

s3 = boto3.client("s3")
bucket_name = "predi-conso-elec-region"
LOCAL_BASE = Path(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive")
S3_BASE = "Predictions"

def file_exists_in_s3(key):
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return True
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise

def upload_file_to_s3(local_path, s3_key):
    if file_exists_in_s3(s3_key):
        print(f"⏭️ Skipped (exists): {s3_key}")
        return
    s3.upload_file(str(local_path), bucket_name, s3_key)
    print(f"✅ Uploaded: {s3_key}")

def upload_all_predictions_and_evals():
    for region_dir in LOCAL_BASE.iterdir():
        if not region_dir.is_dir():
            continue

        for month_dir in region_dir.iterdir():
            if not month_dir.is_dir():
                continue

            for day_dir in month_dir.iterdir():
                if not day_dir.is_dir():
                    continue

                for run_time_dir in day_dir.iterdir():
                    if not run_time_dir.is_dir():
                        continue

                    for folder_name in ["pred", "eval"]:
                        sub_dir = run_time_dir / folder_name
                        if not sub_dir.exists():
                            continue

                        for file in sub_dir.iterdir():
                            if file.is_file():
                                # Build s3 key
                                s3_key = f"{S3_BASE}/{region_dir.name}/{month_dir.name}/{day_dir.name}/{run_time_dir.name}/{folder_name}/{file.name}"
                                upload_file_to_s3(file, s3_key)

def upload_all_monthly_metrics():
    for region_dir in LOCAL_BASE.iterdir():
        if not region_dir.is_dir():
            continue

        for month_dir in region_dir.iterdir():
            if not month_dir.is_dir():
                continue

            for file in month_dir.glob("metrics_master_*.csv"):
                s3_key = f"{S3_BASE}/{region_dir.name}/{month_dir.name}/{file.name}"
                upload_file_to_s3(file, s3_key)

def upload_national_metrics():
    for file in LOCAL_BASE.glob("metrics_master_national_*.csv"):
        s3_key = f"{S3_BASE}/{file.name}"
        upload_file_to_s3(file, s3_key)

def main():
    print("\n🔼 Uploading pred/ and eval/ files...")
    upload_all_predictions_and_evals()
    print(f"✅ Finished uploading pred and eval files")

    print("\n📊 Uploading monthly regional metrics...")
    upload_all_monthly_metrics()
    print(f"✅ Finished uploading monthly metrics files")

    print("\n🌍 Uploading national metrics...")
    upload_national_metrics()
    print(f"✅ Finished uploading national metrics files")

    print("\n🚀 All uploads complete.")

if __name__ == "__main__":
    main()
