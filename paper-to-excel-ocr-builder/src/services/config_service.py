import json
import re
from pathlib import Path
from typing import Any, Dict

class ConfigurationError(Exception):
    pass

class ConfigService:
    def __init__(self, config_dir: str | Path):
        self.config_dir = Path(config_dir)
        self.app_config: Dict[str, Any] = {}
        self.document_type_configs: Dict[str, Any] = {}
        
    def load_configs(self) -> None:
        app_config_path = self.config_dir / "app_config.json"
        doc_config_path = self.config_dir / "document_type_fixed.json"
        
        self.app_config = self._load_json(app_config_path)
        doc_config = self._load_json(doc_config_path)
        
        self._validate_app_config(self.app_config, app_config_path)
        self._validate_document_config(doc_config, doc_config_path)
        
        self.document_type_configs[doc_config.get("document_type", "fixed_form_v1")] = doc_config

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON syntax in {path}: {e}")

    def _validate_app_config(self, config: Dict[str, Any], path: Path) -> None:
        required_keys = ["app_name", "version", "language", "ocr_engine", "server", "excel"]
        for key in required_keys:
            if key not in config:
                raise ConfigurationError(f"Missing required key '{key}' in {path}")
                
        # Ensure cloud_ocr block exists
        if "cloud_ocr" not in config:
            config["cloud_ocr"] = {
                "provider": "gemini",
                "api_key": "",
                "model_name": "gemini-1.5-pro"
            }

    def _validate_document_config(self, config: Dict[str, Any], path: Path) -> None:
        if "fields" not in config or not isinstance(config["fields"], dict):
            raise ConfigurationError(f"Missing or invalid 'fields' in {path}")
            
        fields = config["fields"]
        used_columns = set()
        
        column_regex = re.compile(r"^[A-Za-z]{1,2}$")
        
        for field_key, field_cfg in fields.items():
            if not isinstance(field_cfg, dict):
                raise ConfigurationError(f"Field '{field_key}' must be an object in {path}")
                
            labels = field_cfg.get("labels", [])
            if not isinstance(labels, list) or len(labels) == 0:
                raise ConfigurationError(f"Field '{field_key}' must have at least one label in {path}")
                
            excel_column = field_cfg.get("excel_column")
            if not isinstance(excel_column, str) or not column_regex.match(excel_column):
                raise ConfigurationError(f"Field '{field_key}' has invalid excel_column '{excel_column}' in {path}")
                
            excel_column = excel_column.upper()
            if excel_column in used_columns:
                raise ConfigurationError(f"Duplicate excel_column '{excel_column}' for field '{field_key}' in {path}")
            used_columns.add(excel_column)
            
            region = field_cfg.get("region")
            if region is not None:
                if not isinstance(region, dict):
                    raise ConfigurationError(f"Field '{field_key}' region must be an object in {path}")
                try:
                    x1, y1 = float(region["x1"]), float(region["y1"])
                    x2, y2 = float(region["x2"]), float(region["y2"])
                    if not (0 <= x1 < x2 <= 1):
                        raise ConfigurationError(f"Field '{field_key}' region invalid X coordinates in {path}")
                    if not (0 <= y1 < y2 <= 1):
                        raise ConfigurationError(f"Field '{field_key}' region invalid Y coordinates in {path}")
                except (KeyError, ValueError, TypeError):
                    raise ConfigurationError(f"Field '{field_key}' region invalid or missing coordinates in {path}")
