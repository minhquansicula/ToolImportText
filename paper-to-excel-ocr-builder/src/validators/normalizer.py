import re
from datetime import datetime
from typing import Any, Optional

class Normalizer:
    @staticmethod
    def normalize_date(value: str, date_format: str) -> Optional[datetime]:
        try:
            # Basic parsing based on format (Simplified for demo)
            # Replace common OCR misread of separators
            val = value.strip().replace('-', '/').replace('.', '/')
            return datetime.strptime(val, "%d/%m/%Y")
        except ValueError:
            return None

    @staticmethod
    def normalize_number(value: str) -> Optional[float]:
        try:
            val = value.replace(',', '.')
            val = re.sub(r'\s+', '', val)
            return float(val)
        except ValueError:
            return None

    @staticmethod
    def normalize_text(value: str, preserve_leading_zeros: bool = False) -> str:
        val = value.strip()
        if not preserve_leading_zeros and val.isdigit():
            return str(int(val))
        return val
