"""
Storage utilities for JobBuddy - S3/MinIO wrapper
"""

import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
from fastapi import UploadFile
from app.core.config import settings

class StorageClient:
    """S3/MinIO storage client wrapper"""
    
    def __init__(self):
        """Initialize the storage client"""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL'),  # For MinIO compatibility
            aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
            region_name=os.getenv('S3_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'jobsee-resumes')
        
        # Create bucket if it doesn't exist
        self._create_bucket_if_not_exists()
    
    def _create_bucket_if_not_exists(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            self.s3_client.create_bucket(Bucket=self.bucket_name)
    
    def upload_file(self, file: UploadFile, key: str) -> str:
        """
        Upload a file to S3/MinIO storage
        
        Args:
            file: The file to upload
            key: The key (path) to store the file under
            
        Returns:
            str: The URL of the uploaded file
        """
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            # Generate the file URL
            endpoint_url = os.getenv('S3_ENDPOINT_URL', 'https://s3.amazonaws.com')
            file_url = f"{endpoint_url}/{self.bucket_name}/{key}"
            return file_url
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def download_file(self, key: str, local_path: str) -> bool:
        """
        Download a file from S3/MinIO storage
        
        Args:
            key: The key (path) of the file to download
            local_path: The local path to save the file to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(self.bucket_name, key, local_path)
            return True
        except ClientError:
            return False
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3/MinIO storage
        
        Args:
            key: The key (path) of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for temporary access to a file
        
        Args:
            key: The key (path) of the file
            expiration: Time in seconds for the URL to be valid (default: 1 hour)
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError:
            return None

# For local development without S3/MinIO
class LocalStorageClient:
    """Local file storage client for development"""
    
    def __init__(self):
        """Initialize the local storage client"""
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def upload_file(self, file: UploadFile, key: str) -> str:
        """
        Upload a file to local storage
        
        Args:
            file: The file to upload
            key: The key (path) to store the file under
            
        Returns:
            str: The URL of the uploaded file
        """
        # Create full path
        file_path = os.path.join(self.upload_dir, key)
        
        # Create directories if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Return file URL
        return f"http://localhost:8000/uploads/{key}"
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from local storage
        
        Args:
            key: The key (path) of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.upload_dir, key)
            os.remove(file_path)
            return True
        except OSError:
            return False

# Global storage client instance
# Use local storage if S3 credentials are not provided
if os.getenv('S3_ACCESS_KEY_ID') and os.getenv('S3_SECRET_ACCESS_KEY'):
    storage_client = StorageClient()
else:
    storage_client = LocalStorageClient()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal attacks
    
    Args:
        filename: The original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    
    # Limit length
    filename = filename[:255]
    
    return filename

def generate_file_key(user_id: str, original_filename: str) -> str:
    """
    Generate a unique file key for storage
    
    Args:
        user_id: The user ID
        original_filename: The original filename
        
    Returns:
        str: Generated file key
    """
    import uuid
    from datetime import datetime
    
    # Sanitize the filename
    safe_filename = sanitize_filename(original_filename)
    
    # Get file extension
    _, ext = os.path.splitext(safe_filename)
    
    # Generate unique key
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"resumes/{user_id}/{timestamp}_{unique_id}{ext.lower()}"