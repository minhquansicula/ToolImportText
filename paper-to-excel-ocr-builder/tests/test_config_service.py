import pytest
import json
from pathlib import Path
from src.services.config_service import ConfigService, ConfigurationError

def test_load_valid_configs(config_dir: Path):
    app_config = {
        "app_name": "Test",
        "version": "1.0",
        "language": "vi",
        "ocr_engine": "paddle",
        "server": {},
        "excel": {}
    }
    doc_config = {
        "document_type": "test_doc",
        "fields": {
            "f1": {
                "labels": ["L1"],
                "excel_column": "A"
            }
        }
    }
    
    (config_dir / "app_config.json").write_text(json.dumps(app_config))
    (config_dir / "document_type_fixed.json").write_text(json.dumps(doc_config))
    
    service = ConfigService(config_dir)
    service.load_configs()
    
    assert service.app_config["app_name"] == "Test"
    assert "test_doc" in service.document_type_configs

def test_missing_app_config(config_dir: Path):
    service = ConfigService(config_dir)
    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        service.load_configs()

def test_invalid_json(config_dir: Path):
    (config_dir / "app_config.json").write_text("{invalid")
    (config_dir / "document_type_fixed.json").write_text("{}")
    
    service = ConfigService(config_dir)
    with pytest.raises(ConfigurationError, match="Invalid JSON syntax"):
        service.load_configs()

def test_duplicate_excel_columns(config_dir: Path):
    app_config = {
        "app_name": "Test",
        "version": "1.0",
        "language": "vi",
        "ocr_engine": "paddle",
        "server": {},
        "excel": {}
    }
    doc_config = {
        "document_type": "test_doc",
        "fields": {
            "f1": {
                "labels": ["L1"],
                "excel_column": "A"
            },
            "f2": {
                "labels": ["L2"],
                "excel_column": "A"
            }
        }
    }
    
    (config_dir / "app_config.json").write_text(json.dumps(app_config))
    (config_dir / "document_type_fixed.json").write_text(json.dumps(doc_config))
    
    service = ConfigService(config_dir)
    with pytest.raises(ConfigurationError, match="Duplicate excel_column"):
        service.load_configs()
