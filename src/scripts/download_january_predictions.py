import os
import boto3
from pathlib import Path

def download_predictions_january(s3_bucket, local_base_dir):
    s3 = boto3.client("s3")
    prefix = "Predictions/"
    paginator = s3.get_paginator("list_objects_v2")

    # Filter only January 2025 prediction files in pred folders
    print("🔍 Scanning S3 for January 2025 prediction files...")

    for page in paginator.paginate(Bucket=s3_bucket, Prefix=prefix):
        print(f"found page : {page}")
        for obj in page.get("Contents", []):
            key = obj["Key"]
            parts = key.split("/")
            print(f"len parts is : {len(parts)}")
            print(f"parts[-2] is : {parts[-2]}")
            print(f"parts[-1] is : {parts[-1]}")
            print(f"parts[0] is : {parts[0]}")
            print(f"parts[1] is : {parts[1]}")
            print(f"parts[2] is : {parts[2]}")
            print(f"parts[3] is : {parts[3]}")
            print(f"parts[4] is : {parts[4]}")
            print(f"parts[5] is : {parts[5]}")
            print(f"parts[6] is : {parts[6]}")

            if (
                len(parts) >= 6 and
                parts[2] == "2025-01" and
                parts[5] == "pred" and
                key.endswith(".csv")
            ):
                region_abbr = parts[1]         # e.g., BFC
                print(f"found region_abbr : {region_abbr}")
                month_folder = parts[2]        # 2025-01
                date_folder = parts[3]         # 2025-01-06
                run_time_folder = parts[4]     # e.g., "2"
                filename = parts[-1]           # CSV file

                # Construct local path
                local_folder = os.path.join(
                    local_base_dir,
                    region_abbr,
                    month_folder,
                    date_folder,
                    run_time_folder,
                    "pred"  # Explicit pred subfolder
                )

                print(f"found local_folder : {local_folder}")

                os.makedirs(local_folder, exist_ok=True)
                local_path = os.path.join(local_folder, filename)

                try:
                    s3.download_file(s3_bucket, key, local_path)
                    print(f"✅ Downloaded: {key} → {local_path}")
                except Exception as e:
                    print(f"❌ Failed to download {key}: {e}")


if __name__ == "__main__":
    s3_bucket = "predi-conso-elec-region"
    local_base_dir = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"
    
    download_predictions_january(s3_bucket, local_base_dir)
