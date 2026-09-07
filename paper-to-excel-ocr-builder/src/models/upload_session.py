from dataclasses import dataclass
from datetime import datetime

@dataclass
class UploadSession:
    token: str
    created_at: datetime
    expires_at: datetime
