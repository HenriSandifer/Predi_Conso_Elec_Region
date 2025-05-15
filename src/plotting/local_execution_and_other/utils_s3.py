import os
import boto3
import pandas as pd
from io import StringIO

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

def write_html_plot_to_s3(fig, s3_key):
    """
    Description

    """
        
    try:
        html_buffer = StringIO()
        fig.write_html(html_buffer)
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=html_buffer.getvalue(), ContentType='text/html')
        print(f"✅ Plot written to: s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print(f"❌ Error writing to S3: s3://{S3_BUCKET}/{s3_key}\n{e}")


def write_json_plot_to_s3(plot_data, s3_key, content_type="application/json"):
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=plot_data,
        ContentType=content_type
    )

