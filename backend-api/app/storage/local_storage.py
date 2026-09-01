"""
Local file storage module to replace Google Cloud Storage functionality.
This module provides local file access for development without GCP dependencies.
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import base64
import hashlib
import hmac
import json
import posixpath
import time
import urllib.parse


class LocalStorage:
    """
    Local storage handler that mimics Google Cloud Storage signed URL functionality.
    Files are served from a local directory structure.
    """
    
    def __init__(self, base_path: str = "/code/local_storage"):
        """
        Initialize local storage with a base path.
        
        Args:
            base_path: Root directory for local file storage
        """
        self.base_path = Path(base_path)

    def _safe_path(self, bucket_name: str, blob_name: str) -> Path:
        if not bucket_name or bucket_name.startswith(("/", "\\")):
            raise ValueError("Invalid bucket name")
        normalized_blob = posixpath.normpath(blob_name.replace("\\", "/"))
        if normalized_blob.startswith("../") or normalized_blob == ".." or normalized_blob.startswith("/"):
            raise ValueError("Invalid blob path")
        path = (self.base_path / bucket_name / normalized_blob).resolve()
        storage_root = self.base_path.resolve()
        if storage_root not in path.parents and path != storage_root:
            raise ValueError("Resolved path escapes storage root")
        return path
    
    def generate_signed_url(
        self, 
        bucket_name: str, 
        blob_name: str, 
        expiration: timedelta = timedelta(seconds=3600),
        method: str = "GET"
    ) -> str:
        """
        Generate a local file URL that mimics GCS signed URLs.
        In local mode, this returns a direct file path or API endpoint.
        
        Args:
            bucket_name: Bucket name (used as subdirectory)
            blob_name: File path within bucket
            expiration: URL expiration time (ignored in local mode)
            method: HTTP method (ignored in local mode)
            
        Returns:
            Local file URL/path
        """
        # Validate the path without touching the filesystem. Upload operations
        # are responsible for creating directories.
        self._safe_path(bucket_name, blob_name)
        
        encoded_path = base64.urlsafe_b64encode(f"{bucket_name}/{blob_name}".encode()).decode()
        expires = int(time.time() + expiration.total_seconds())
        signature = self.sign_encoded_path(encoded_path, expires)
        
        # Return a local API endpoint URL
        query = urllib.parse.urlencode({"expires": expires, "signature": signature})
        return f"/api/v1/local-storage/{encoded_path}?{query}"

    @staticmethod
    def _signing_key() -> str:
        return (
            os.getenv("LOCAL_STORAGE_SIGNING_KEY")
            or os.getenv("BACKEND_API_JWT_SECRET")
            or os.getenv("VHVL_SIGNING_KEY")
            or os.getenv("API_SERVICE_TOKEN")
            or ""
        )

    def sign_encoded_path(self, encoded_path: str, expires: int) -> str:
        secret = self._signing_key()
        if not secret:
            return ""
        payload = f"{encoded_path}.{expires}".encode("utf-8")
        return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    def verify_signed_url(self, encoded_path: str, expires: Optional[int], signature: Optional[str]) -> bool:
        if not expires or not signature or expires < int(time.time()):
            return False
        expected = self.sign_encoded_path(encoded_path, expires)
        return bool(expected) and hmac.compare_digest(expected, signature)
    
    def get_file_path(self, bucket_name: str, blob_name: str) -> Path:
        """
        Get the actual file system path for a blob.
        
        Args:
            bucket_name: Bucket name (subdirectory)
            blob_name: File path within bucket
            
        Returns:
            Full file system path
        """
        return self._safe_path(bucket_name, blob_name)
    
    def file_exists(self, bucket_name: str, blob_name: str) -> bool:
        """
        Check if a file exists in local storage.
        
        Args:
            bucket_name: Bucket name
            blob_name: File path within bucket
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.get_file_path(bucket_name, blob_name)
        return file_path.exists() and file_path.is_file()
    
    def upload_file(self, bucket_name: str, blob_name: str, file_data: bytes) -> bool:
        """
        Upload/save a file to local storage.
        
        Args:
            bucket_name: Bucket name (subdirectory)
            blob_name: File path within bucket
            file_data: File content as bytes
            
        Returns:
            True if successful
        """
        file_path = self.get_file_path(bucket_name, blob_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return True
    
    def decode_signed_url_path(self, encoded_path: str) -> tuple[str, str]:
        """
        Decode the encoded path from a local signed URL.
        
        Args:
            encoded_path: Base64 encoded bucket/blob path
            
        Returns:
            Tuple of (bucket_name, blob_name)
        """
        decoded = base64.urlsafe_b64decode(encoded_path.encode()).decode()
        parts = decoded.split('/', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid encoded path: {encoded_path}")


# Singleton instance for use across the application
_local_storage_instance: Optional[LocalStorage] = None


def get_local_storage() -> LocalStorage:
    """
    Get the singleton LocalStorage instance.
    
    Returns:
        LocalStorage instance
    """
    global _local_storage_instance
    if _local_storage_instance is None:
        base_path = os.getenv('LOCAL_STORAGE_PATH', '/code/local_storage')
        _local_storage_instance = LocalStorage(base_path)
    return _local_storage_instance
