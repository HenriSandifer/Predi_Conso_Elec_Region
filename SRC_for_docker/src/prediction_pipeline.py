import boto3
import pandas as pd
from io import BytesIO

def load_s3_csv(bucket, object_name):
    """Loads CSV file from S3 into a Pandas DataFrame"""
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=object_name)
    return pd.read_csv(BytesIO(response['Body'].read()))

# Load the latest processed data
df_test = load_s3_csv('energy-predictions-storage', 'processed_data/latest.csv')
