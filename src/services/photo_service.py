"""Photo storage and processing service."""

import io
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image

from ..core.config import get_settings
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class PhotoService:
    """Service for photo storage and processing."""
    
    def __init__(self) -> None:
        self.storage_type = settings.storage_type
        self.local_storage_path = Path("uploads/photos")
        self._setup_storage()
    
    def _setup_storage(self) -> None:
        """Set up storage backend."""
        if self.storage_type == "local":
            # Create local directories
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            (self.local_storage_path / "originals").mkdir(exist_ok=True)
            (self.local_storage_path / "thumbnails").mkdir(exist_ok=True)
            logger.info("Local photo storage initialized", path=str(self.local_storage_path))
        elif self.storage_type == "s3":
            # Initialize S3 client if configured
            try:
                import boto3
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region,
                )
                self.s3_bucket = settings.aws_bucket_name
                logger.info("S3 photo storage initialized", bucket=self.s3_bucket)
            except Exception as e:
                logger.error("Failed to initialize S3", error=str(e))
                # Fall back to local storage
                self.storage_type = "local"
                self._setup_storage()
    
    async def save_photo(
        self,
        photo_data: bytes,
        user_id: str,
        food_id: str,
        content_type: str = "image/jpeg",
    ) -> Optional[Tuple[str, str]]:
        """
        Save photo and return URLs for original and thumbnail.
        
        Returns:
            Tuple of (original_url, thumbnail_url) or None if failed
        """
        try:
            # Generate unique filename
            file_extension = self._get_extension_from_content_type(content_type)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{user_id}_{food_id}_{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            # Process image
            original_data, thumbnail_data = await self._process_image(photo_data)
            
            if self.storage_type == "local":
                return await self._save_local(filename, original_data, thumbnail_data)
            elif self.storage_type == "s3":
                return await self._save_s3(filename, original_data, thumbnail_data, content_type)
            
            return None
            
        except Exception as e:
            logger.error(
                "Error saving photo",
                user_id=user_id,
                food_id=food_id,
                error=str(e),
                exc_info=True,
            )
            return None
    
    async def _process_image(
        self,
        photo_data: bytes,
        max_size: int = 1024 * 1024,  # 1MB
        thumbnail_size: Tuple[int, int] = (300, 300),
    ) -> Tuple[bytes, bytes]:
        """Process image: compress and create thumbnail."""
        try:
            # Open image
            img = Image.open(io.BytesIO(photo_data))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = rgb_img
            
            # Compress original if too large
            original_io = io.BytesIO()
            quality = 95
            img.save(original_io, format="JPEG", quality=quality, optimize=True)
            
            # Reduce quality until under max_size
            while original_io.tell() > max_size and quality > 30:
                original_io = io.BytesIO()
                quality -= 10
                img.save(original_io, format="JPEG", quality=quality, optimize=True)
            
            original_data = original_io.getvalue()
            
            # Create thumbnail
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            thumbnail_io = io.BytesIO()
            img.save(thumbnail_io, format="JPEG", quality=85, optimize=True)
            thumbnail_data = thumbnail_io.getvalue()
            
            logger.info(
                "Image processed",
                original_size=len(photo_data),
                compressed_size=len(original_data),
                thumbnail_size=len(thumbnail_data),
                quality=quality,
            )
            
            return original_data, thumbnail_data
            
        except Exception as e:
            logger.error("Error processing image", error=str(e), exc_info=True)
            # Return original if processing fails
            return photo_data, photo_data
    
    async def _save_local(
        self,
        filename: str,
        original_data: bytes,
        thumbnail_data: bytes,
    ) -> Optional[Tuple[str, str]]:
        """Save photos to local storage."""
        try:
            # Save original
            original_path = self.local_storage_path / "originals" / filename
            with open(original_path, "wb") as f:
                f.write(original_data)
            
            # Save thumbnail
            thumb_filename = f"thumb_{filename}"
            thumbnail_path = self.local_storage_path / "thumbnails" / thumb_filename
            with open(thumbnail_path, "wb") as f:
                f.write(thumbnail_data)
            
            # Return relative URLs (would be served by static file server)
            original_url = f"/uploads/photos/originals/{filename}"
            thumbnail_url = f"/uploads/photos/thumbnails/{thumb_filename}"
            
            logger.info(
                "Photos saved locally",
                original=str(original_path),
                thumbnail=str(thumbnail_path),
            )
            
            return original_url, thumbnail_url
            
        except Exception as e:
            logger.error("Error saving photos locally", error=str(e), exc_info=True)
            return None
    
    async def _save_s3(
        self,
        filename: str,
        original_data: bytes,
        thumbnail_data: bytes,
        content_type: str,
    ) -> Optional[Tuple[str, str]]:
        """Save photos to S3."""
        try:
            if not hasattr(self, "s3_client"):
                logger.error("S3 client not initialized")
                return None
            
            # Upload original
            original_key = f"photos/originals/{filename}"
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=original_key,
                Body=original_data,
                ContentType=content_type,
                CacheControl="max-age=31536000",  # 1 year cache
            )
            
            # Upload thumbnail
            thumb_filename = f"thumb_{filename}"
            thumbnail_key = f"photos/thumbnails/{thumb_filename}"
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=thumbnail_key,
                Body=thumbnail_data,
                ContentType=content_type,
                CacheControl="max-age=31536000",
            )
            
            # Generate URLs
            region = settings.aws_region
            original_url = f"https://{self.s3_bucket}.s3.{region}.amazonaws.com/{original_key}"
            thumbnail_url = f"https://{self.s3_bucket}.s3.{region}.amazonaws.com/{thumbnail_key}"
            
            logger.info(
                "Photos saved to S3",
                original_key=original_key,
                thumbnail_key=thumbnail_key,
            )
            
            return original_url, thumbnail_url
            
        except Exception as e:
            logger.error("Error saving photos to S3", error=str(e), exc_info=True)
            return None
    
    async def delete_photo(self, photo_url: str) -> bool:
        """Delete a photo from storage."""
        try:
            if self.storage_type == "local":
                # Extract filename from URL
                filename = photo_url.split("/")[-1]
                
                # Try to delete both original and thumbnail
                for subdir in ["originals", "thumbnails"]:
                    file_path = self.local_storage_path / subdir / filename
                    if file_path.exists():
                        file_path.unlink()
                        logger.info("Photo deleted", path=str(file_path))
                
                return True
                
            elif self.storage_type == "s3":
                if not hasattr(self, "s3_client"):
                    return False
                
                # Extract key from URL
                key = photo_url.split(f"{self.s3_bucket}.s3.")[1].split(".amazonaws.com/")[1]
                
                self.s3_client.delete_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                )
                
                logger.info("Photo deleted from S3", key=key)
                return True
                
        except Exception as e:
            logger.error("Error deleting photo", photo_url=photo_url, error=str(e))
            return False
    
    async def get_photo_urls_from_telegram(
        self,
        file_id: str,
        bot_token: str,
    ) -> Optional[Tuple[str, str]]:
        """Download photo from Telegram and save to storage."""
        try:
            import httpx
            
            # Get file info from Telegram
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{bot_token}/getFile",
                    params={"file_id": file_id},
                )
                response.raise_for_status()
                file_info = response.json()
                
                if not file_info.get("ok"):
                    logger.error("Failed to get file info from Telegram")
                    return None
                
                file_path = file_info["result"]["file_path"]
                
                # Download file
                download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                response = await client.get(download_url)
                response.raise_for_status()
                
                photo_data = response.content
                
                logger.info(
                    "Downloaded photo from Telegram",
                    file_id=file_id,
                    size=len(photo_data),
                )
                
                return photo_data
                
        except Exception as e:
            logger.error(
                "Error downloading photo from Telegram",
                file_id=file_id,
                error=str(e),
                exc_info=True,
            )
            return None
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type."""
        extensions = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return extensions.get(content_type.lower(), ".jpg")
    
    async def cleanup_old_photos(self, days: int = 30) -> int:
        """Clean up photos older than specified days (background task)."""
        try:
            if self.storage_type == "local":
                count = 0
                cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
                
                for subdir in ["originals", "thumbnails"]:
                    dir_path = self.local_storage_path / subdir
                    for file_path in dir_path.glob("*"):
                        if file_path.stat().st_mtime < cutoff_date:
                            file_path.unlink()
                            count += 1
                
                logger.info(f"Cleaned up {count} old photos")
                return count
                
            # S3 cleanup would use lifecycle policies instead
            return 0
            
        except Exception as e:
            logger.error("Error cleaning up old photos", error=str(e), exc_info=True)
            return 0