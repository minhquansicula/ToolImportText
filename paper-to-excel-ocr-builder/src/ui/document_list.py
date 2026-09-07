from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel

class DocumentListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("Danh sách chứng từ")
        self.layout.addWidget(self.label)
        
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
    def add_document(self, name: str):
        self.list_widget.addItem(name)
