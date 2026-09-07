import time
from collections import deque
from threading import Lock

class UploadRateLimiter:
    def __init__(self, max_uploads_per_minute: int = 10, max_concurrent: int = 3):
        self.max_uploads_per_minute = max_uploads_per_minute
        self.max_concurrent = max_concurrent
        self.upload_timestamps = deque()
        self.current_concurrent = 0
        self.lock = Lock()

    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            # Clean up old timestamps
            while self.upload_timestamps and now - self.upload_timestamps[0] > 60:
                self.upload_timestamps.popleft()
                
            if len(self.upload_timestamps) >= self.max_uploads_per_minute:
                return False
                
            if self.current_concurrent >= self.max_concurrent:
                return False
                
            self.upload_timestamps.append(now)
            self.current_concurrent += 1
            return True

    def release(self) -> None:
        with self.lock:
            if self.current_concurrent > 0:
                self.current_concurrent -= 1
