from dataclasses import dataclass
from typing import Any

@dataclass
class ValidationResult:
    is_valid: bool
    normalized_value: Any
    error_message: str | None = None
    warning_message: str | None = None
    requires_manual_review: bool = False
