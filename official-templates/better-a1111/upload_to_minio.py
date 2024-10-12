import os
import boto3
from botocore.client import Config

# MinIO configuration
minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'https://s3.madiator.com')
minio_access_key = os.environ.get('MINIO_ACCESS_KEY', '')
minio_secret_key = os.environ.get('MINIO_SECRET_KEY', '')
minio_bucket = os.environ.get('MINIO_BUCKET', 'better')

# File to upload
file_path = '/ba1111.tar.zst'
object_name = 'ba1111/ba1111.tar.zst'

# Get file size
file_size = os.path.getsize(file_path)

# Create a client with the MinIO configuration
s3_client = boto3.client('s3',
                         endpoint_url=minio_endpoint,
                         aws_access_key_id=minio_access_key,
                         aws_secret_access_key=minio_secret_key,
                         config=Config(signature_version='s3v4'),
                         region_name='us-east-1')

# Upload the file
try:
    s3_client.upload_file(file_path, minio_bucket, object_name)
    print(f"File {file_path} uploaded successfully to {minio_bucket}/{object_name}")
    print(f"File size: {file_size} bytes")
except Exception as e:
    print(f"Error uploading file: {str(e)}")