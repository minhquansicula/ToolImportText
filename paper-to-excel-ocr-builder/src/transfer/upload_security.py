import uuid
import PIL.Image
from pathlib import Path
from typing import Tuple

class ImageValidationError(Exception):
    pass

class UploadSecurity:
    def __init__(self, allowed_extensions: list[str], allowed_mime_types: list[str], 
                 max_size_mb: int, max_width: int, max_height: int, max_pixel_count: int):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        self.allowed_mime_types = allowed_mime_types
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_width = max_width
        self.max_height = max_height
        self.max_pixel_count = max_pixel_count
        
        # Prevent decompression bombs
        PIL.Image.MAX_IMAGE_PIXELS = max_pixel_count

    def validate_file_metadata(self, filename: str, content_type: str, file_size: int) -> None:
        if file_size > self.max_size_bytes:
            raise ImageValidationError(f"File size exceeds maximum allowed ({self.max_size_bytes} bytes).")
            
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise ImageValidationError(f"File extension {ext} not allowed.")
            
        if content_type not in self.allowed_mime_types:
            raise ImageValidationError(f"MIME type {content_type} not allowed.")

    def validate_image_content(self, file_path: Path) -> None:
        import PIL.ImageOps
        try:
            with PIL.Image.open(file_path) as img:
                img.verify()  # Verify it's an image
                
            # Reopen to check dimensions, as verify() doesn't load data
            with PIL.Image.open(file_path) as img:
                orig_format = img.format or "JPEG"
                # Fix EXIF rotation (mobile photos appear upright)
                img = PIL.ImageOps.exif_transpose(img)
                
                width, height = img.size
                if width > self.max_width or height > self.max_height:
                    raise ImageValidationError(f"Image dimensions ({width}x{height}) exceed maximum allowed.")
                    
                if getattr(img, "is_animated", False):
                    raise ImageValidationError("Animated images are not supported.")
                
                # Save the properly oriented image back to disk
                if orig_format.upper() in ["JPEG", "JPG"]:
                    img.save(file_path, format=orig_format, quality=95)
                else:
                    img.save(file_path, format=orig_format)
                    
        except PIL.Image.DecompressionBombError:
            raise ImageValidationError("Image exceeds maximum pixel count (Decompression Bomb protection).")
        except Exception as e:
            if isinstance(e, ImageValidationError):
                raise
            raise ImageValidationError(f"Invalid or corrupted image: {str(e)}")

    def generate_safe_filename(self, original_filename: str) -> str:
        ext = Path(original_filename).suffix.lower()
        # Fallback to .jpg if no extension
        if not ext or ext not in self.allowed_extensions:
            ext = ".jpg"
        return f"{uuid.uuid4().hex}{ext}"
