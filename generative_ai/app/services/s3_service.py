# app/services/s3_service.py

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import UploadFile, HTTPException, status

from app.core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, S3_BUCKET_NAME

# Initialize S3 client globally when the module is imported
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION_NAME:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME
        )
        print(f"S3 client initialized for region: {AWS_REGION_NAME}")
    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found. S3 uploads will not work.")
        s3_client = None
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        s3_client = None
else:
    print("AWS S3 environment variables not fully set. S3 uploads will not work.")


async def upload_file_to_s3(file: UploadFile, object_key: str) -> str:
    """
    Uploads a file to the configured S3 bucket.

    Args:
        file: The UploadFile object from the FastAPI request.
        object_key: The desired key (path) in the S3 bucket.

    Returns:
        The S3 URL of the uploaded file.

    Raises:
        HTTPException: If S3 is not configured or upload fails.
    """
    if s3_client is None or S3_BUCKET_NAME is None:
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="S3 storage is not configured on the server.")

    try:
        s3_client.upload_fileobj(
            file.file,      # The file-like object from UploadFile
            S3_BUCKET_NAME, # The bucket name
            object_key      # The S3 key (path)
        )
        print(f"Successfully uploaded file to s3://{S3_BUCKET_NAME}/{object_key}")
        s3_url = f"s3://{S3_BUCKET_NAME}/{object_key}"
        return s3_url

    except (NoCredentialsError, PartialCredentialsError):
         print("AWS credentials not configured properly.")
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AWS credentials not configured.")
    except ClientError as e:
         print(f"S3 upload failed: {e}")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file to storage: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during S3 upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during upload: {e}")
    finally:
        # IMPORTANT: Close the uploaded file stream after processing
        await file.close()
async def delete_file_from_s3(object_key: str):
    """
    Deletes a file from the configured S3 bucket.

    Args:
        object_key: The key (path) of the object in the S3 bucket.

    Raises:
        HTTPException: If S3 is not configured or delete fails (excluding 404).
    """
    if s3_client is None or S3_BUCKET_NAME is None:
         # If S3 is not configured, maybe we should still allow DB delete?
         # Or perhaps raise an error depending on business rules.
         # For now, raise an error.
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="S3 storage is not configured on the server.")

    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=object_key)
        print(f"Successfully deleted S3 object: {object_key}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            print(f"Warning: S3 object {object_key} not found (already deleted or incorrect key). Proceeding with DB delete.")
            # Don't raise an HTTPException for 404 from S3 delete
            pass
        else:
            print(f"S3 delete failed for {object_key}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file from storage: {e}")
    except (NoCredentialsError, PartialCredentialsError):
         print("AWS credentials not configured properly.")
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AWS credentials not configured.")
    except Exception as e:
        print(f"An unexpected error occurred during S3 delete for {object_key}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during delete: {e}")
