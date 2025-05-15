# streamlit_src/io/io_s3.py

import os
import boto3
import json

S3_BUCKET = os.getenv("MY_PROJECT_BUCKET", "predi-conso-elec-region")
s3 = boto3.client("s3")

def read_json_from_s3(key):
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = response["Body"].read().decode("utf-8")
        return content
    except Exception as e:
        print(f"❌ Error reading JSON from s3://{S3_BUCKET}/{key}:\n{e}")
        return None

def list_s3_objects(prefix):
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]
    except Exception as e:
        print(f"❌ Error listing S3 objects under s3://{S3_BUCKET}/{prefix}:\n{e}")
        return []
