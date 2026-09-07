from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .validation_result import ValidationResult

class FieldStatus(Enum):
    VALID = "Hợp lệ"
    INVALID = "Lỗi"
    NEEDS_REVIEW = "Cần kiểm tra"

@dataclass
class FieldData:
    raw_value: str
    confidence: float
    validation_result: ValidationResult
    source: str
    edited_value: str | None = None
    manually_reviewed: bool = False

    @property
    def current_value(self) -> Any:
        return self.edited_value if self.edited_value is not None else self.validation_result.normalized_value

@dataclass
class DocumentData:
    document_type: str
    fields: dict[str, FieldData] = field(default_factory=dict)
