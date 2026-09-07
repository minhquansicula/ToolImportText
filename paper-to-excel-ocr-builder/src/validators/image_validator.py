import PIL.Image
from pathlib import Path

class ImageValidator:
    """Validator for checking if an image is completely valid before OCR."""
    def __init__(self, max_width: int = 8000, max_height: int = 8000):
        self.max_width = max_width
        self.max_height = max_height

    def validate(self, image_path: Path) -> bool:
        try:
            with PIL.Image.open(image_path) as img:
                img.verify()
            
            with PIL.Image.open(image_path) as img:
                w, h = img.size
                if w > self.max_width or h > self.max_height:
                    return False
            return True
        except Exception:
            return False
