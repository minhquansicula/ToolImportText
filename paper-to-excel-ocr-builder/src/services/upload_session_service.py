import secrets
from datetime import datetime, timedelta
from typing import Optional
from src.models.upload_session import UploadSession

class SessionError(Exception):
    pass

class UploadSessionService:
    def __init__(self, expiration_minutes: int = 15):
        self.expiration_minutes = expiration_minutes
        self._current_session: Optional[UploadSession] = None

    def create_session(self) -> UploadSession:
        token = secrets.token_urlsafe(32)
        now = datetime.now()
        expires = now + timedelta(minutes=self.expiration_minutes)
        self._current_session = UploadSession(token=token, created_at=now, expires_at=expires)
        return self._current_session

    def invalidate_session(self) -> None:
        self._current_session = None

    def validate_token(self, token: str) -> bool:
        if self._current_session is None:
            return False
            
        if datetime.now() > self._current_session.expires_at:
            return False
            
        return secrets.compare_digest(self._current_session.token, token)
        
    def get_remaining_seconds(self) -> int:
        if self._current_session is None:
            return 0
        diff = (self._current_session.expires_at - datetime.now()).total_seconds()
        return max(0, int(diff))
