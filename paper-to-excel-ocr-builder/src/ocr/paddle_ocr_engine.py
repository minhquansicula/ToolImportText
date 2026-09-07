import logging
from pathlib import Path
from typing import List, Any
from src.models.ocr_result import OCRResult, BoundingBox
from src.ocr.base_ocr_engine import BaseOCREngine

logger = logging.getLogger(__name__)

class PaddleOCREngine(BaseOCREngine):
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.ocr = None
        
    def initialize(self) -> None:
        try:
            from paddleocr import PaddleOCR
            # Disable noisy logging
            import logging as pd_logging
            pd_logging.getLogger('ppocr').setLevel(logging.ERROR)
            
            # Map config
            lang = self.config.get("lang", "vi")
            use_angle_cls = self.config.get("use_angle_cls", True)
            use_gpu = self.config.get("use_gpu", False)
            
            det_model_dir = self.config.get("det_model_dir")
            rec_model_dir = self.config.get("rec_model_dir")
            cls_model_dir = self.config.get("cls_model_dir")
            
            kwargs = {
                "lang": lang,
                "use_angle_cls": True,
                "show_log": False,
                "det_db_unclip_ratio": 1.6,
                "det_db_box_thresh": 0.5,
                "ocr_version": "PP-OCRv4"
            }
            if det_model_dir: kwargs["det_model_dir"] = det_model_dir
            if rec_model_dir: kwargs["rec_model_dir"] = rec_model_dir
            if cls_model_dir: kwargs["cls_model_dir"] = cls_model_dir
            
            self.ocr = PaddleOCR(**kwargs)
            logger.info("PaddleOCR engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise RuntimeError(f"OCR Initialization Error: {e}")

    def extract_text(self, image_path: Path | str) -> List[OCRResult]:
        if not self.ocr:
            self.initialize()
            
        results = []
        try:
            import cv2
            import numpy as np
            
            # Read image with OpenCV
            # We use cv2.imdecode to support paths with unicode/special characters on Windows
            path_bytes = np.fromfile(str(image_path), dtype=np.uint8)
            img = cv2.imdecode(path_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError(f"Không thể đọc ảnh: {image_path}")
                
            # Resize image to speed up CPU inference (max side length 1500)
            MAX_SIDE = 1500
            h, w = img.shape[:2]
            scale = 1.0
            
            if max(h, w) > MAX_SIDE:
                scale = MAX_SIDE / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # PaddleOCR returns [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], ('text', confidence)]
            raw_result = self.ocr.ocr(img, cls=True)
            if not raw_result or not raw_result[0]:
                return results
                
            sequence = 0
            for line in raw_result[0]:
                if not line or len(line) != 2:
                    continue
                    
                box_points, (text, confidence) = line
                # Scale boxes back to original size
                original_box_points = [(float(p[0]) / scale, float(p[1]) / scale) for p in box_points]
                box = BoundingBox(points=original_box_points)
                
                results.append(OCRResult(
                    text=text,
                    confidence=float(confidence),
                    bounding_box=box,
                    sequence_number=sequence,
                    source_image=str(image_path)
                ))
                sequence += 1
                
            return results
        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            raise
