from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt

class OCRResultViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.tab_raw = QTextEdit()
        self.tab_raw.setReadOnly(True)
        self.tabs.addTab(self.tab_raw, "Raw Text")
        
        self.tab_kv = QTextEdit()
        self.tab_kv.setReadOnly(True)
        self.tabs.addTab(self.tab_kv, "Key Value")
        
        self.tab_table = QTextEdit()
        self.tab_table.setReadOnly(True)
        self.tabs.addTab(self.tab_table, "Table (TSV)")
        
        self.layout.addWidget(self.tabs)
        
        # Copy Buttons
        btn_layout = QHBoxLayout()
        self.btn_copy_all = QPushButton("Copy All (Current Tab)")
        self.btn_copy_all.clicked.connect(self.copy_current_tab)
        btn_layout.addWidget(self.btn_copy_all)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)
        
    def copy_current_tab(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, QTextEdit):
            text = current_widget.toPlainText()
            QApplication.clipboard().setText(text)
            
    def update_data(self, data: dict):
        # Sort by line number to preserve document order
        sorted_items = sorted(data.items(), key=lambda x: x[1].get('order', 0))
        
        # 1. Raw Text Mode — shows text exactly like the original document
        raw_text = "\n".join([v.get('raw_value', '') for _, v in sorted_items])
        self.tab_raw.setPlainText(raw_text)
        
        # 2. Key Value Mode — shows line numbers with text
        kv_lines = []
        for i, (_, v) in enumerate(sorted_items, 1):
            text = v.get('raw_value', '')
            conf = v.get('confidence', 0)
            kv_lines.append(f"[{i:02d}] {text}")
        self.tab_kv.setPlainText("\n".join(kv_lines))
        
        # 3. Table Mode (TSV format) — one row per line
        rows = ["STT\tNội dung"]
        for i, (_, v) in enumerate(sorted_items, 1):
            rows.append(f"{i}\t{v.get('raw_value', '')}")
        self.tab_table.setPlainText("\n".join(rows))

