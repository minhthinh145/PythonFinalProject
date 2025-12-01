"""
AWS S3 Service - Upload, download, and manage files in S3
Used for tài liệu học tập storage
"""
from typing import Optional, Dict, Any, BinaryIO
from decouple import config
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Lazy-load boto3
_s3_client = None


def get_s3_client():
    """Get S3 client (singleton pattern)"""
    global _s3_client
    
    if _s3_client is None:
        try:
            import boto3
            from botocore.config import Config
            
            aws_access_key = config('AWS_ACCESS_KEY_ID', default=None)
            aws_secret_key = config('AWS_SECRET_ACCESS_KEY', default=None)
            aws_region = config('AWS_REGION', default='ap-southeast-2')
            
            if not aws_access_key or not aws_secret_key:
                logger.warning("AWS credentials not configured, S3 features disabled")
                return None
            
            _s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region,
                config=Config(
                    signature_version='s3v4',
                    connect_timeout=5,
                    read_timeout=10,
                )
            )
            
            logger.info("✅ S3 client initialized successfully")
            
        except ImportError:
            logger.error("❌ boto3 not installed. Run: pip install boto3")
            return None
        except Exception as e:
            logger.error(f"❌ S3 client initialization failed: {e}")
            _s3_client = None
            return None
    
    return _s3_client


class S3Service:
    """
    AWS S3 Service for file operations
    
    Structure:
    - tai-lieu/{lop_hoc_phan_id}/{filename}
    - temp/{uuid}  (temporary uploads)
    """
    
    def __init__(self):
        self.client = get_s3_client()
        self.bucket_name = config('AWS_S3_BUCKET_NAME', default='hcmue-tailieu-hoctap-20251029')
        self.base_url = config('AWS_S3_BASE_URL', default=f'https://{self.bucket_name}.s3.ap-southeast-2.amazonaws.com')
        self.region = config('AWS_REGION', default='ap-southeast-2')
    
    @property
    def is_available(self) -> bool:
        """Check if S3 is available"""
        return self.client is not None
    
    # ============ UPLOAD OPERATIONS ============
    
    def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        lop_hoc_phan_id: str,
        content_type: str = 'application/octet-stream',
        metadata: Dict = None
    ) -> Optional[Dict[str, str]]:
        """
        Upload a file to S3
        
        Args:
            file_obj: File-like object
            filename: Original filename
            lop_hoc_phan_id: ID of lớp học phần
            content_type: MIME type
            metadata: Additional metadata
        
        Returns:
            Dict with 'key' and 'url' or None on failure
        """
        if not self.is_available:
            logger.error("S3 not available")
            return None
        
        try:
            # Generate unique key
            ext = filename.split('.')[-1] if '.' in filename else ''
            unique_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Clean filename
            safe_filename = self._sanitize_filename(filename)
            
            # S3 key path
            s3_key = f"tai-lieu/{lop_hoc_phan_id}/{timestamp}_{unique_id}_{safe_filename}"
            
            # Metadata
            extra_args = {
                'ContentType': content_type,
                'Metadata': metadata or {}
            }
            
            # Upload
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            url = f"{self.base_url}/{s3_key}"
            
            logger.info(f"✅ File uploaded: {s3_key}")
            
            return {
                'key': s3_key,
                'url': url,
                'filename': filename,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return None
    
    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        lop_hoc_phan_id: str,
        content_type: str = 'application/octet-stream'
    ) -> Optional[Dict[str, str]]:
        """Upload bytes directly"""
        from io import BytesIO
        file_obj = BytesIO(data)
        return self.upload_file(file_obj, filename, lop_hoc_phan_id, content_type)
    
    # ============ DOWNLOAD OPERATIONS ============
    
    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for downloading
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration in seconds (default 1 hour)
        
        Returns:
            Presigned URL or None
        """
        if not self.is_available:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def get_public_url(self, s3_key: str) -> str:
        """Get public URL (if bucket allows public access)"""
        return f"{self.base_url}/{s3_key}"
    
    def download_file(self, s3_key: str) -> Optional[bytes]:
        """Download file content"""
        if not self.is_available:
            return None
        
        try:
            from io import BytesIO
            
            buffer = BytesIO()
            self.client.download_fileobj(
                self.bucket_name,
                s3_key,
                buffer
            )
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    # ============ DELETE OPERATIONS ============
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        if not self.is_available:
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"✅ File deleted: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def delete_files(self, s3_keys: list) -> bool:
        """Delete multiple files"""
        if not self.is_available:
            return False
        
        try:
            objects = [{'Key': key} for key in s3_keys]
            
            self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': objects}
            )
            
            logger.info(f"✅ Deleted {len(s3_keys)} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete files: {e}")
            return False
    
    # ============ LIST OPERATIONS ============
    
    def list_files(self, prefix: str, max_keys: int = 100) -> list:
        """List files with a given prefix"""
        if not self.is_available:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': self.get_public_url(obj['Key'])
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def list_tai_lieu_by_lop(self, lop_hoc_phan_id: str) -> list:
        """List tài liệu for a lớp học phần"""
        prefix = f"tai-lieu/{lop_hoc_phan_id}/"
        return self.list_files(prefix)
    
    # ============ UTILITY METHODS ============
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for S3"""
        import re
        # Remove special characters, keep alphanumeric, dash, underscore, dot
        safe = re.sub(r'[^\w\-_\.]', '_', filename)
        return safe[:200]  # Limit length
    
    def get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for S3 connection"""
        if not self.is_available:
            return {
                'status': 'unavailable',
                'message': 'S3 not configured or connection failed'
            }
        
        try:
            # Try to list bucket
            self.client.head_bucket(Bucket=self.bucket_name)
            return {
                'status': 'healthy',
                'bucket': self.bucket_name,
                'region': self.region
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


# Singleton instance
_s3_service = None


def get_s3_service() -> S3Service:
    """Get S3 service singleton"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
