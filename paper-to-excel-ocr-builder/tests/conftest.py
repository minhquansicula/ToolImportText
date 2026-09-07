import pytest
from pathlib import Path

@pytest.fixture
def workspace_dir(tmp_path: Path) -> Path:
    return tmp_path / "workspace"

@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    config_d = tmp_path / "config"
    config_d.mkdir()
    return config_d
