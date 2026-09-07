import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from src.services.file_service import FileService
from src.workers.processing_queue import ProcessingQueue
from src.models.processing_item import ProcessingItem, ProcessingStatus

logger = logging.getLogger(__name__)

class InboxHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_created(self, event):
        if not event.is_directory:
            self.watcher.handle_new_file(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self.watcher.handle_new_file(Path(event.src_path))

class InboxWatcher:
    def __init__(self, file_service: FileService, processing_queue: ProcessingQueue,
                 check_interval: float = 1.0, max_attempts: int = 3, ignored_extensions: list = None):
        self.file_service = file_service
        self.processing_queue = processing_queue
        self.check_interval = check_interval
        self.max_attempts = max_attempts
        self.ignored_extensions = ignored_extensions or [".tmp", ".part", ".partial"]
        
        self.observer = None
        self.processed_files = set()

    def start(self):
        self.observer = Observer()
        handler = InboxHandler(self)
        self.observer.schedule(handler, str(self.file_service.inbox_dir), recursive=False)
        self.observer.start()
        logger.info("Inbox watcher started.")
        self._scan_existing_files()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Inbox watcher stopped.")

    def _scan_existing_files(self):
        for file_path in self.file_service.inbox_dir.iterdir():
            if file_path.is_file():
                self.handle_new_file(file_path)

    def handle_new_file(self, file_path: Path):
        if file_path.name in self.processed_files:
            return
            
        ext = file_path.suffix.lower()
        if ext in self.ignored_extensions or file_path.name.startswith("."):
            return
            
        self.processed_files.add(file_path.name)
        
        # Stability check
        if not self._wait_for_stability(file_path):
            logger.warning(f"File {file_path.name} is unstable or vanished.")
            return
            
        try:
            # Check for duplicate
            file_hash = self.file_service.calculate_file_hash(file_path)
            if self.processing_queue.is_duplicate_hash(file_hash):
                logger.info(f"Duplicate file detected: {file_path.name}")
                self.file_service.move_to_failed(file_path)
                return
                
            # Move to processing
            new_path = self.file_service.move_to_processing(file_path)
            
            # Create ProcessingItem
            from datetime import datetime
            item = ProcessingItem(
                file_id=new_path.stem,
                file_path=str(new_path),
                source="Local", 
                import_time=datetime.now(),
                status=ProcessingStatus.UNPROCESSED
            )
            
            self.processing_queue.add_item(item, file_hash)
            logger.info(f"File {file_path.name} moved to processing queue.")
            
        except Exception as e:
            logger.error(f"Error handling file {file_path.name}: {e}")
            try:
                self.file_service.move_to_failed(file_path)
            except:
                pass

    def _wait_for_stability(self, file_path: Path) -> bool:
        attempts = 0
        last_size = -1
        last_mtime = -1
        
        while attempts < self.max_attempts:
            if not file_path.exists():
                return False
                
            try:
                stat = file_path.stat()
                current_size = stat.st_size
                current_mtime = stat.st_mtime
                
                if current_size == last_size and current_mtime == last_mtime:
                    return True
                    
                last_size = current_size
                last_mtime = current_mtime
            except Exception:
                pass
                
            time.sleep(self.check_interval)
            attempts += 1
            
        return False
