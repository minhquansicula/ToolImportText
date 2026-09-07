import pytest
from pathlib import Path
from src.services.file_service import FileService

def test_ensure_directories(workspace_dir: Path):
    service = FileService(workspace_dir)
    assert (workspace_dir / "Inbox").exists()
    assert (workspace_dir / "Processing").exists()
    assert (workspace_dir / "Processed").exists()
    assert (workspace_dir / "Failed").exists()
    assert (workspace_dir / "Backup").exists()
    assert (workspace_dir / "Output").exists()
    assert (workspace_dir / "Models").exists()
    assert (workspace_dir / "Logs").exists()

def test_calculate_file_hash(workspace_dir: Path):
    service = FileService(workspace_dir)
    test_file = workspace_dir / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("hello world")
    
    hash_val = service.calculate_file_hash(test_file)
    assert hash_val == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

def test_move_to_processing(workspace_dir: Path):
    service = FileService(workspace_dir)
    inbox = workspace_dir / "Inbox"
    test_file = inbox / "test.jpg"
    test_file.write_text("data")
    
    dest_file = service.move_to_processing(test_file)
    assert dest_file.exists()
    assert dest_file.parent.name == "Processing"
    assert not test_file.exists()
