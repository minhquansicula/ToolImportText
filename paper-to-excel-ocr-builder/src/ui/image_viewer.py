from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #e0e0e0;")
        
        self.label = QLabel("Chưa chọn ảnh")
        self.label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.label)
        
        self.layout.addWidget(self.scroll_area)
        self.current_path = None
        
    def set_image(self, path: str):
        self.current_path = path
        self._update_image()
            
    def _update_image(self):
        if not self.current_path:
            return
            
        pixmap = QPixmap(self.current_path)
        if not pixmap.isNull():
            # Scale to fit the scroll area width/height
            scaled_pixmap = pixmap.scaled(
                self.scroll_area.width() - 20, 
                self.scroll_area.height() - 20, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap)
        else:
            self.label.setText("Lỗi: Không thể tải ảnh")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image()
