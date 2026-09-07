from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.models.ocr_result import OCRResult

class BaseExtractor(ABC):
    @abstractmethod
    def extract_fields(self, ocr_results: List[OCRResult], config: Dict[str, Any]) -> Dict[str, Any]:
        pass
