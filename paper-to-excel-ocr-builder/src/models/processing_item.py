from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ProcessingStatus(Enum):
    RECEIVED = "Đã nhận"
    UNPROCESSED = "Chưa xử lý"
    PROCESSING = "Đang xử lý"
    REVIEW_REQUIRED = "Cần kiểm tra"
    VALID = "Hợp lệ"
    ROW_MATCHED = "Đã tìm dòng"
    COMPLETED = "Đã hoàn thành"
    FAILED = "Lỗi"
    DUPLICATE = "Trùng lặp"
    NO_MATCH_FOUND = "Không tìm thấy"

@dataclass
class ProcessingItem:
    file_id: str
    file_path: str
    source: str
    import_time: datetime
    status: ProcessingStatus
    ocr_status: str | None = None
    review_status: str | None = None
    completion_status: str | None = None
    error_summary: str | None = None
