import re
from typing import Any, Dict
from src.models.validation_result import ValidationResult
from src.validators.normalizer import Normalizer

class FieldValidator:
    def validate(self, field_config: Dict[str, Any], raw_value: str, confidence: float, threshold: float = 0.85) -> ValidationResult:
        required = field_config.get("required", False)
        if not raw_value.strip():
            if required:
                return ValidationResult(False, None, "Trường bắt buộc không được để trống", requires_manual_review=True)
            return ValidationResult(True, None)

        requires_review = confidence < threshold
        normalized = raw_value
        
        regex = field_config.get("regex")
        if regex:
            if not re.match(regex, raw_value.strip()):
                return ValidationResult(False, None, f"Không đúng định dạng: {regex}", requires_manual_review=True)

        if field_config.get("numeric", False):
            val = Normalizer.normalize_number(raw_value)
            if val is None:
                return ValidationResult(False, None, "Phải là số hợp lệ", requires_manual_review=True)
            normalized = val

        date_format = field_config.get("date_format")
        if date_format:
            val = Normalizer.normalize_date(raw_value, date_format)
            if val is None:
                return ValidationResult(False, None, f"Ngày không đúng định dạng {date_format}", requires_manual_review=True)
            normalized = val.strftime("%d/%m/%Y")

        if not field_config.get("numeric") and not field_config.get("date_format"):
            preserve_zeros = field_config.get("preserve_leading_zeros", False)
            normalized = Normalizer.normalize_text(raw_value, preserve_zeros)

        return ValidationResult(True, normalized, requires_manual_review=requires_review)
