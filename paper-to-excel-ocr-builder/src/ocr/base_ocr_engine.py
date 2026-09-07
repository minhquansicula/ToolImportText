from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from src.models.ocr_result import OCRResult

class BaseOCREngine(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass
        
    @abstractmethod
    def extract_text(self, image_path: Path | str) -> List[OCRResult]:
        pass
