from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import json
from pathlib import Path

class SettingsDialog(QDialog):
    def __init__(self, config_dir: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt OCR")
        self.setMinimumWidth(400)
        
        self.config_dir = config_dir
        self.config_path = config_dir / "app_config.json"
        
        self.layout = QVBoxLayout(self)
        
        # Engine selection
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel("Động cơ OCR (OCR Engine):"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("AI Cục bộ (PaddleOCR)", "paddleocr")
        self.engine_combo.addItem("AI Đám mây (OpenRouter/Gemini)", "cloud_ocr")
        engine_layout.addWidget(self.engine_combo)
        self.layout.addLayout(engine_layout)
        
        # API Key
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("OpenRouter/Gemini API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_input)
        self.layout.addLayout(api_layout)
        
        # Model Name
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Tên Model (vd: google/gemini-1.5-flash):"))
        self.model_name_input = QLineEdit()
        model_layout.addWidget(self.model_name_input)
        self.layout.addLayout(model_layout)
        
        # Save Button
        self.btn_save = QPushButton("Lưu cài đặt")
        self.btn_save.clicked.connect(self.save_settings)
        self.layout.addWidget(self.btn_save)
        
        self.load_settings()
        
    def load_settings(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                
            engine = self.config.get("ocr_engine", "paddleocr")
            idx = self.engine_combo.findData(engine)
            if idx >= 0:
                self.engine_combo.setCurrentIndex(idx)
                
            cloud_cfg = self.config.get("cloud_ocr", {})
            self.api_key_input.setText(cloud_cfg.get("api_key", ""))
            self.model_name_input.setText(cloud_cfg.get("model_name", "google/gemini-3.5-flash"))
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải cài đặt: {e}")
            self.config = {}
            
    def save_settings(self):
        self.config["ocr_engine"] = self.engine_combo.currentData()
        if "cloud_ocr" not in self.config:
            self.config["cloud_ocr"] = {}
        self.config["cloud_ocr"]["api_key"] = self.api_key_input.text()
        self.config["cloud_ocr"]["model_name"] = self.model_name_input.text()
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Thành công", "Đã lưu cài đặt. Bạn có thể cần chạy lại OCR để cập nhật.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu cài đặt: {e}")
