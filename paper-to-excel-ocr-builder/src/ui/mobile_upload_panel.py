from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap

class MobileUploadPanel(QWidget):
    start_requested = Signal()
    stop_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Server Status: Đã dừng")
        self.layout.addWidget(self.status_label)
        
        self.url_label = QLabel("URL: Chưa khởi động")
        self.layout.addWidget(self.url_label)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.qr_label)
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Bắt đầu")
        self.btn_start.clicked.connect(self.start_requested.emit)
        
        self.btn_stop = QPushButton("Dừng")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        self.btn_stop.setEnabled(False)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        self.layout.addLayout(btn_layout)
        
    def set_running(self, is_running: bool, url: str = ""):
        if is_running:
            self.status_label.setText("Server Status: Đang chạy")
            self.url_label.setText(f"URL: {url}")
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self._generate_qr(url)
        else:
            self.status_label.setText("Server Status: Đã dừng")
            self.url_label.setText("URL: Chưa khởi động")
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.qr_label.clear()
            
    def _generate_qr(self, url: str):
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qimage = ImageQt(img)
        pixmap = QPixmap.fromImage(qimage)
        self.qr_label.setPixmap(pixmap)
