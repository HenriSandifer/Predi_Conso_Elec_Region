import boto3

# Initialize S3 client
s3 = boto3.client('s3')
bucket_name = 'predi-conso-elec-region'

def upload_to_s3(file_name, bucket, object_name=None):
    """Uploads a file to an S3 bucket"""
    if object_name is None:
        object_name = file_name
    s3.upload_file(file_name, bucket, object_name)
    print(f"Uploaded {file_name} to s3://{bucket}/{object_name}")

# Example usage
upload_to_s3("data/raw_data_2025-03-12.csv", bucket_name, "raw_data/2025-03-12.csv")
