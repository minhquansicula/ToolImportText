from typing import Dict, Any, List, Optional
from src.models.ocr_result import OCRResult, BoundingBox
from src.extractors.base_extractor import BaseExtractor
import numpy as np

class FixedFormExtractor(BaseExtractor):
    def extract_fields(self, ocr_results: List[OCRResult], config: Dict[str, Any]) -> Dict[str, Any]:
        extracted = {}
        fields = config.get("fields", {})
        
        # Build spatial index or just use linear search for now
        # Calculate image dimensions if possible (heuristic from max coords)
        if not ocr_results:
            return {k: {"raw_value": "", "confidence": 0.0, "source": "empty"} for k in fields.keys()}
            
        max_x = max(r.bounding_box.x_max for r in ocr_results)
        max_y = max(r.bounding_box.y_max for r in ocr_results)
        
        for field_key, field_cfg in fields.items():
            region = field_cfg.get("region")
            if region:
                # Extract by region (relative coordinates)
                abs_region = {
                    "x1": region["x1"] * max_x,
                    "y1": region["y1"] * max_y,
                    "x2": region["x2"] * max_x,
                    "y2": region["y2"] * max_y,
                }
                match = self._find_in_region(ocr_results, abs_region)
                if match:
                    extracted[field_key] = {
                        "raw_value": match.text,
                        "confidence": match.confidence,
                        "source": "region"
                    }
                else:
                    extracted[field_key] = {"raw_value": "", "confidence": 0.0, "source": "region"}
            else:
                # Extract by labels
                labels = field_cfg.get("labels", [])
                match = self._find_by_labels(ocr_results, labels)
                if match:
                    extracted[field_key] = {
                        "raw_value": match.text,
                        "confidence": match.confidence,
                        "source": "label"
                    }
                else:
                    extracted[field_key] = {"raw_value": "", "confidence": 0.0, "source": "label"}
                    
        return extracted
        
    def _find_in_region(self, ocr_results: List[OCRResult], abs_region: Dict[str, float]) -> Optional[OCRResult]:
        # Find results whose center is within the region
        candidates = []
        for r in ocr_results:
            cx, cy = r.bounding_box.center
            if (abs_region["x1"] <= cx <= abs_region["x2"] and 
                abs_region["y1"] <= cy <= abs_region["y2"]):
                candidates.append(r)
                
        if not candidates:
            return None
            
        # If multiple, sort by Y then X, and join
        candidates.sort(key=lambda r: (r.bounding_box.y_min, r.bounding_box.x_min))
        text = " ".join(c.text for c in candidates)
        conf = sum(c.confidence for c in candidates) / len(candidates)
        # Create a synthetic merged result
        return OCRResult(text, conf, candidates[0].bounding_box, 0, "")
        
    def _find_by_labels(self, ocr_results: List[OCRResult], labels: List[str]) -> Optional[OCRResult]:
        label_lower = [l.lower() for l in labels]
        
        for i, r in enumerate(ocr_results):
            text_lower = r.text.lower().strip()
            # If the label exactly matches the text, or text starts with label + colon
            for lbl in label_lower:
                if text_lower == lbl or text_lower.startswith(f"{lbl}:") or text_lower.startswith(lbl):
                    # Value might be in the same box "Label: Value"
                    if ":" in r.text:
                        parts = r.text.split(":", 1)
                        if len(parts) > 1 and parts[1].strip():
                            return OCRResult(parts[1].strip(), r.confidence, r.bounding_box, r.sequence_number, r.source_image)
                    
                    # Or it might be the next box to the right or below
                    # Simple heuristic: next sequence number if it's on the same line roughly
                    if i + 1 < len(ocr_results):
                        next_r = ocr_results[i+1]
                        # Check if roughly same Y
                        if abs(next_r.bounding_box.center[1] - r.bounding_box.center[1]) < next_r.bounding_box.height:
                            return next_r
        return None
