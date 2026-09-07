from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSplitter
from PySide6.QtCore import Qt
from src.ui.image_viewer import ImageViewer
from src.ui.ocr_result_viewer import OCRResultViewer
from src.ui.mobile_upload_panel import MobileUploadPanel
from src.ui.document_list import DocumentListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paper to Text OCR Assistant")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Toolbar
        self.toolbar_layout = QHBoxLayout()
        self.btn_select_image = QPushButton("Chọn ảnh")
        self.btn_run_ocr = QPushButton("Chạy OCR")
        self.btn_export_txt = QPushButton("Export TXT")
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_settings = QPushButton("Cài đặt")
        
        self.toolbar_layout.addWidget(self.btn_select_image)
        self.toolbar_layout.addWidget(self.btn_run_ocr)
        self.toolbar_layout.addWidget(self.btn_export_txt)
        self.toolbar_layout.addWidget(self.btn_export_csv)
        self.toolbar_layout.addWidget(self.btn_export_json)
        self.toolbar_layout.addWidget(self.btn_settings)
        self.toolbar_layout.addStretch()
        self.layout.addLayout(self.toolbar_layout)
        
        # Main Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Left Panel (Mobile Upload + Doc List)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.mobile_upload = MobileUploadPanel()
        self.document_list = DocumentListWidget()
        self.left_layout.addWidget(self.mobile_upload)
        self.left_layout.addWidget(self.document_list)
        self.splitter.addWidget(self.left_panel)
        
        # Center Panel (Image Viewer)
        self.image_viewer = ImageViewer()
        self.splitter.addWidget(self.image_viewer)
        
        # Right Panel (OCR Result)
        self.result_viewer = OCRResultViewer()
        self.splitter.addWidget(self.result_viewer)
        
        self.splitter.setSizes([300, 600, 400])
