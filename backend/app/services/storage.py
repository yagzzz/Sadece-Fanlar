"""
Storage service for file uploads (MinIO/S3)
"""
import io
import uuid
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path
import hashlib

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from PIL import Image

from app.core.config import settings


class StorageService:
    """Service for file storage using MinIO/S3"""
    
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
        self.bucket = settings.minio_bucket
    
    async def ensure_bucket(self):
        """Ensure the bucket exists"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
    
    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate a unique filename"""
        ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        
        if prefix:
            return f"{prefix}/{timestamp}/{unique_id}{ext}"
        return f"{timestamp}/{unique_id}{ext}"
    
    async def upload_file(
        self,
        file: UploadFile,
        prefix: str = "",
        allowed_types: list = None,
        max_size: int = None,
    ) -> dict:
        """
        Upload a file to storage
        Returns file info including URL
        """
        await self.ensure_bucket()
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        max_allowed = max_size or (settings.max_upload_size_mb * 1024 * 1024)
        if file_size > max_allowed:
            raise ValueError(f"Dosya çok büyük. Maksimum: {max_allowed // (1024*1024)}MB")
        
        # Validate type
        if allowed_types and file.content_type not in allowed_types:
            raise ValueError(f"Bu dosya türü desteklenmiyor: {file.content_type}")
        
        # Generate filename
        filename = self._generate_filename(file.filename, prefix)
        
        # Upload
        self.client.put_object(
            self.bucket,
            filename,
            io.BytesIO(content),
            file_size,
            content_type=file.content_type,
        )
        
        return {
            "url": self._get_url(filename),
            "filename": filename,
            "original_filename": file.filename,
            "file_size": file_size,
            "mime_type": file.content_type,
        }
    
    async def upload_image(
        self,
        file: UploadFile,
        prefix: str = "",
        max_width: int = 2000,
        max_height: int = 2000,
        quality: int = 85,
        create_thumbnail: bool = True,
        thumbnail_size: Tuple[int, int] = (400, 400),
        create_blur: bool = False,
    ) -> dict:
        """
        Upload and process an image
        Returns image info with URLs for original, thumbnail, and blur
        """
        await self.ensure_bucket()
        
        # Validate type
        allowed = settings.allowed_image_types
        if file.content_type not in allowed:
            raise ValueError("Bu resim formatı desteklenmiyor")
        
        # Read and process image
        content = await file.read()
        img = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Get original dimensions
        width, height = img.size
        
        # Resize if too large
        if width > max_width or height > max_height:
            img.thumbnail((max_width, max_height), Image.LANCZOS)
        
        # Save original
        filename = self._generate_filename(file.filename, prefix)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        self.client.put_object(
            self.bucket,
            filename,
            buffer,
            buffer.getbuffer().nbytes,
            content_type='image/jpeg',
        )
        
        result = {
            "url": self._get_url(filename),
            "filename": filename,
            "original_filename": file.filename,
            "file_size": buffer.getbuffer().nbytes,
            "mime_type": "image/jpeg",
            "width": img.size[0],
            "height": img.size[1],
        }
        
        # Create thumbnail
        if create_thumbnail:
            thumb = img.copy()
            thumb.thumbnail(thumbnail_size, Image.LANCZOS)
            
            thumb_filename = filename.replace('.', '_thumb.')
            thumb_buffer = io.BytesIO()
            thumb.save(thumb_buffer, format='JPEG', quality=75, optimize=True)
            thumb_buffer.seek(0)
            
            self.client.put_object(
                self.bucket,
                thumb_filename,
                thumb_buffer,
                thumb_buffer.getbuffer().nbytes,
                content_type='image/jpeg',
            )
            
            result["thumbnail_url"] = self._get_url(thumb_filename)
        
        # Create blur for PPV preview
        if create_blur:
            blur = img.copy()
            blur.thumbnail((100, 100), Image.LANCZOS)
            blur = blur.resize(img.size, Image.LANCZOS)
            
            from PIL import ImageFilter
            blur = blur.filter(ImageFilter.GaussianBlur(radius=20))
            
            blur_filename = filename.replace('.', '_blur.')
            blur_buffer = io.BytesIO()
            blur.save(blur_buffer, format='JPEG', quality=50, optimize=True)
            blur_buffer.seek(0)
            
            self.client.put_object(
                self.bucket,
                blur_filename,
                blur_buffer,
                blur_buffer.getbuffer().nbytes,
                content_type='image/jpeg',
            )
            
            result["blur_url"] = self._get_url(blur_filename)
        
        return result
    
    async def delete_file(self, filename: str) -> bool:
        """Delete a file from storage"""
        try:
            self.client.remove_object(self.bucket, filename)
            return True
        except S3Error:
            return False
    
    def _get_url(self, filename: str) -> str:
        """Get public URL for a file.

        Tarayıcının erişebilmesi için minio_public_url tercih edilir; aksi halde
        (yalnızca aynı ağdan erişilebilen) minio_endpoint kullanılır.
        """
        if settings.minio_public_url:
            base = settings.minio_public_url.rstrip("/")
            return f"{base}/{self.bucket}/{filename}"
        protocol = "https" if settings.minio_use_ssl else "http"
        return f"{protocol}://{settings.minio_endpoint}/{self.bucket}/{filename}"
    
    async def get_presigned_url(
        self,
        filename: str,
        expires_seconds: int = 3600,
    ) -> str:
        """Get a presigned URL for temporary access"""
        from datetime import timedelta
        
        url = self.client.presigned_get_object(
            self.bucket,
            filename,
            expires=timedelta(seconds=expires_seconds),
        )
        return url


# Singleton instance
storage_service = StorageService()


# Helper function for use in routes
async def upload_file(file: UploadFile, prefix: str = "") -> str:
    """Simple helper to upload a file and return URL"""
    result = await storage_service.upload_file(file, prefix)
    return result["url"]
