import os
import shutil
import hashlib
from pathlib import Path

class FileService:
    def __init__(self, workspace_dir: str | Path):
        self.workspace_dir = Path(workspace_dir)
        self.inbox_dir = self.workspace_dir / "Inbox"
        self.processing_dir = self.workspace_dir / "Processing"
        self.processed_dir = self.workspace_dir / "Processed"
        self.failed_dir = self.workspace_dir / "Failed"
        self.backup_dir = self.workspace_dir / "Backup"
        self.output_dir = self.workspace_dir / "Output"
        self.models_dir = self.workspace_dir / "Models"
        self.logs_dir = self.workspace_dir / "Logs"
        
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        directories = [
            self.inbox_dir, self.processing_dir, self.processed_dir,
            self.failed_dir, self.backup_dir, self.output_dir,
            self.models_dir, self.logs_dir
        ]
        for d in directories:
            d.mkdir(parents=True, exist_ok=True)

    def calculate_file_hash(self, file_path: str | Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def move_file(self, src: str | Path, dest_dir: str | Path, new_name: str | None = None) -> Path:
        src_path = Path(src)
        dest_dir_path = Path(dest_dir)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
            
        dest_dir_path.mkdir(parents=True, exist_ok=True)
        
        final_name = new_name if new_name else src_path.name
        dest_path = dest_dir_path / final_name
        
        shutil.move(str(src_path), str(dest_path))
        return dest_path

    def move_to_processing(self, src: str | Path) -> Path:
        return self.move_file(src, self.processing_dir)

    def move_to_processed(self, src: str | Path) -> Path:
        return self.move_file(src, self.processed_dir)

    def move_to_failed(self, src: str | Path) -> Path:
        return self.move_file(src, self.failed_dir)
