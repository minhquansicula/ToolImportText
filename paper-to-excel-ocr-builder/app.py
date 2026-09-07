import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import Slot, QThread, Signal, QObject

from src.ui.main_window import MainWindow
from src.services.upload_session_service import UploadSessionService
from src.transfer.upload_security import UploadSecurity
from src.transfer.upload_rate_limiter import UploadRateLimiter
from src.services.file_service import FileService
from src.transfer.local_upload_server import LocalUploadServer
from src.services.export_service import ExportService
from src.ocr.paddle_ocr_engine import PaddleOCREngine

import json

class SimpleOCRThread(QThread):
    finished_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self, image_path, config_dir: Path):
        super().__init__()
        self.image_path = image_path
        self.config_dir = config_dir
        
    def run(self):
        try:
            # Read config
            config_path = self.config_dir / "app_config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                app_config = json.load(f)
                
            engine_type = app_config.get("ocr_engine", "paddleocr")
            
            if engine_type == "cloud_ocr":
                from src.ocr.cloud_ocr_engine import CloudOCREngine
                engine = CloudOCREngine(app_config.get("cloud_ocr", {}))
            else:
                from src.ocr.paddle_ocr_engine import PaddleOCREngine
                engine = PaddleOCREngine(app_config.get("paddleocr", {}))
                
            engine.initialize()
            results = engine.extract_text(self.image_path)
            
            # Format output for UI — preserve original document order
            data = {}
            for i, res in enumerate(results):
                data[f"line_{i}"] = {"raw_value": res.text, "confidence": res.confidence, "order": i}
                
            self.finished_signal.emit(data)
        except Exception as e:
            self.error_signal.emit(str(e))

class AppSignals(QObject):
    file_received = Signal(str)

class AppController:
    def __init__(self, window: MainWindow):
        self.window = window
        self.workspace = Path("./workspace")
        self.file_service = FileService(self.workspace)
        
        self.signals = AppSignals()
        self.signals.file_received.connect(self.on_file_received)
        
        self.session_service = UploadSessionService()
        self.security = UploadSecurity(
            allowed_extensions=[".jpg", ".png", ".webp", ".jpeg"],
            allowed_mime_types=["image/jpeg", "image/png", "image/webp"],
            max_size_mb=15, max_width=8000, max_height=8000, max_pixel_count=40000000
        )
        self.rate_limiter = UploadRateLimiter()
        
        self.upload_server = LocalUploadServer(
            port=8265,
            session_service=self.session_service,
            security=self.security,
            rate_limiter=self.rate_limiter,
            file_service=self.file_service
        )
        self.upload_server.on_upload_success = lambda fname: self.signals.file_received.emit(fname)
        
        self.current_image_path = None
        self.current_ocr_data = {}
        
        # Connect UI signals
        self.window.btn_select_image.clicked.connect(self.select_image)
        self.window.btn_run_ocr.clicked.connect(self.run_ocr)
        self.window.btn_export_txt.clicked.connect(lambda: self.export_data("txt"))
        self.window.btn_export_csv.clicked.connect(lambda: self.export_data("csv"))
        self.window.btn_export_json.clicked.connect(lambda: self.export_data("json"))
        self.window.btn_settings.clicked.connect(self.open_settings)
        
        self.window.mobile_upload.start_requested.connect(self.start_server)
        self.window.mobile_upload.stop_requested.connect(self.stop_server)
        
    @Slot()
    def open_settings(self):
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(Path("./config"), self.window)
        dialog.exec()
        
    @Slot()
    def start_server(self):
        try:
            url = self.upload_server.start()
            session = self.session_service.create_session()
            full_url = f"{url}/upload/{session.token}"
            self.window.mobile_upload.set_running(True, full_url)
        except Exception as e:
            QMessageBox.critical(self.window, "Lỗi", f"Không thể khởi động server:\n{str(e)}")

    @Slot()
    def stop_server(self):
        self.upload_server.stop()
        self.window.mobile_upload.set_running(False)
        
    @Slot(str)
    def on_file_received(self, filename: str):
        full_path = str(self.file_service.inbox_dir / filename)
        self.current_image_path = full_path
        self.window.image_viewer.set_image(full_path)
        self.window.document_list.add_document(filename)
        QMessageBox.information(self.window, "Nhận ảnh", f"Đã nhận ảnh mới từ điện thoại:\n{filename}")
        
    @Slot()
    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Chọn ảnh OCR", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_name:
            self.current_image_path = file_name
            self.window.image_viewer.set_image(file_name)
            self.window.document_list.add_document(Path(file_name).name)
            
    @Slot()
    def run_ocr(self):
        if not self.current_image_path:
            QMessageBox.warning(self.window, "Cảnh báo", "Vui lòng chọn ảnh trước khi chạy OCR.")
            return
            
        self.window.btn_run_ocr.setEnabled(False)
        self.window.btn_run_ocr.setText("Đang chạy OCR...")
        
        self.ocr_thread = SimpleOCRThread(self.current_image_path, Path("./config"))
        self.ocr_thread.finished_signal.connect(self.on_ocr_finished)
        self.ocr_thread.error_signal.connect(self.on_ocr_error)
        self.ocr_thread.start()
        
    @Slot(dict)
    def on_ocr_finished(self, data):
        self.window.btn_run_ocr.setEnabled(True)
        self.window.btn_run_ocr.setText("Chạy OCR")
        self.current_ocr_data = data
        self.window.result_viewer.update_data(data)
        QMessageBox.information(self.window, "Thành công", "Chạy OCR hoàn tất!")
        
    @Slot(str)
    def on_ocr_error(self, error_msg):
        self.window.btn_run_ocr.setEnabled(True)
        self.window.btn_run_ocr.setText("Chạy OCR")
        QMessageBox.critical(self.window, "Lỗi", f"Lỗi OCR:\n{error_msg}")
        
    def export_data(self, fmt: str):
        if not self.current_ocr_data:
            QMessageBox.warning(self.window, "Cảnh báo", "Không có dữ liệu để xuất.")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(self.window, "Lưu file", f"export.{fmt}", f"{fmt.upper()} Files (*.{fmt})")
        if file_name:
            path = Path(file_name)
            try:
                if fmt == "txt": ExportService.export_txt(self.current_ocr_data, path)
                elif fmt == "csv": ExportService.export_csv(self.current_ocr_data, path)
                elif fmt == "json": ExportService.export_json(self.current_ocr_data, path)
                QMessageBox.information(self.window, "Thành công", f"Đã xuất file {fmt.upper()} thành công!")
            except Exception as e:
                QMessageBox.critical(self.window, "Lỗi", f"Lỗi khi xuất file:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = AppController(window)
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
