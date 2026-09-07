import cv2
import numpy as np
from pathlib import Path

class ImagePreprocessor:
    def __init__(self, profile: str = "default"):
        self.profile = profile

    def process(self, image_path: Path | str, output_path: Path | str) -> Path:
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
            
        if self.profile == "grayscale":
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif self.profile == "enhanced":
            # Grayscale -> CLAHE -> Denoise
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            img = cv2.fastNlMeansDenoising(enhanced, h=30)
            
        cv2.imwrite(str(output_path), img)
        return Path(output_path)
