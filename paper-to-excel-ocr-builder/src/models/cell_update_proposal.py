from dataclasses import dataclass
from enum import Enum
from typing import Any

class CellState(Enum):
    MISSING = "MISSING"
    ALREADY_COMPLETE = "ALREADY_COMPLETE"
    CONFLICT = "CONFLICT"
    OCR_VALUE_MISSING = "OCR_VALUE_MISSING"
    INVALID_OCR_VALUE = "INVALID_OCR_VALUE"
    NOT_UPDATABLE = "NOT_UPDATABLE"
    FORMULA_CELL = "FORMULA_CELL"

class CellAction(Enum):
    FILL = "Điền"
    KEEP = "Giữ nguyên"
    MANUAL = "Nhập tay"
    SKIP = "Bỏ qua"
    RESOLVE = "Xử lý"

@dataclass
class CellUpdateProposal:
    field_name: str
    excel_column: str
    current_value: Any
    ocr_value: Any
    confidence: float
    state: CellState
    action: CellAction
