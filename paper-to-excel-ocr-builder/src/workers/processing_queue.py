import threading
from queue import Queue
from typing import List, Optional
from src.models.processing_item import ProcessingItem, ProcessingStatus

class ProcessingQueue:
    def __init__(self):
        self._queue = Queue()
        self._items: dict[str, ProcessingItem] = {}
        self._seen_hashes = set()
        self._lock = threading.Lock()
        
    def add_item(self, item: ProcessingItem, file_hash: str):
        with self._lock:
            self._items[item.file_id] = item
            self._seen_hashes.add(file_hash)
        self._queue.put(item.file_id)
        
    def is_duplicate_hash(self, file_hash: str) -> bool:
        with self._lock:
            return file_hash in self._seen_hashes
            
    def get_next_item(self, timeout: float = None) -> Optional[ProcessingItem]:
        try:
            file_id = self._queue.get(timeout=timeout)
            with self._lock:
                return self._items.get(file_id)
        except Exception:
            return None
            
    def mark_done(self):
        self._queue.task_done()
        
    def update_status(self, file_id: str, status: ProcessingStatus, **kwargs):
        with self._lock:
            if file_id in self._items:
                item = self._items[file_id]
                item.status = status
                for k, v in kwargs.items():
                    if hasattr(item, k):
                        setattr(item, k, v)
                        
    def get_all_items(self) -> List[ProcessingItem]:
        with self._lock:
            return list(self._items.values())
