# 📄 Paper to Text OCR Assistant

An intelligent desktop tool designed to convert scanned paper documents and images into digital text. Features multi-format export (`TXT`, `CSV`, `JSON`), seamless wireless photo upload from mobile devices via QR code on local networks, and versatile OCR engine choices (Offline PaddleOCR & Cloud Vision AI via OpenRouter/Gemini).

---

## ✨ Key Features

- **🔍 Flexible OCR Engines:**
  - **Local AI (Offline):** Powered by PaddleOCR for local processing without requiring an Internet connection or third-party API costs.
  - **Cloud AI:** Integrates with OpenRouter / Gemini API utilizing high-performance vision models (e.g. Gemini 2.5 Flash, 1.5 Pro) for superior accuracy with complex layouts, multi-language/Vietnamese text, and handwritten notes.
- **📱 Wireless Mobile Capture (QR Code Upload):**
  - Built-in lightweight FastAPI server generates a session QR code.
  - Scan with any smartphone camera to snap and transfer photos directly to your PC without cables, messengers, or image compression.
- **📋 Interactive Viewer & Inline Editing:**
  - Sleek 3-column layout: Upload list, zoomable image inspector, and interactive OCR line results.
  - Allows reviewing and editing recognized text lines prior to exporting.
- **💾 Multi-format Export:**
  - Plain text: `.txt`
  - Spreadsheets: `.csv`
  - Structured data: `.json`

---

## 📂 Project Structure

```text
ToolImportText/
├── .gitignore
├── README.md
└── paper-to-excel-ocr-builder/
    ├── app.py                      # Main desktop application entry point (PySide6)
    ├── build.bat                   # Batch build script for PyInstaller executable
    ├── requirements.txt            # Python dependencies
    ├── config/
    │   ├── app_config.example.json # Template configuration (sanitized, no API keys)
    │   └── document_type_fixed.json
    ├── src/
    │   ├── ocr/                    # OCR engines (PaddleOCR, Cloud AI OpenRouter/Gemini)
    │   ├── services/               # File management, export, session, QR code helpers
    │   ├── transfer/               # Local server, security & rate-limiting for mobile upload
    │   ├── ui/                     # Desktop GUI components (PySide6)
    │   ├── validators/             # Data validation and text normalization
    │   └── web/                    # Mobile capture web portal
    └── workspace/                  # Local runtime workspace (ignored by Git)
```

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
- **OS:** Windows 10 / 11
- **Python:** Version 3.10 or 3.11 recommended

### 2. Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/minhquansicula/ToolImportText.git
   cd ToolImportText/paper-to-excel-ocr-builder
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   pip install PySide6 openpyxl
   ```
   *(Optional: For local offline OCR, install `paddlepaddle` and `paddleocr`)*.

### 3. Configuration & API Key Setup
1. Duplicate the template config file in `paper-to-excel-ocr-builder/config/`:
   ```powershell
   copy config\app_config.example.json config\app_config.json
   ```

2. Provide your API key using **either method**:
   - **Method 1 (Recommended):** Open the application, click **"Cài đặt" (Settings)** on the toolbar, and paste your API key into the input field.
   - **Method 2:** Set an environment variable:
     ```powershell
     $env:OPENROUTER_API_KEY="your_key_here"
     # or
     $env:GEMINI_API_KEY="your_key_here"
     ```

### 4. Running the Application
Launch the app with:
```bash
python app.py
```

---

## 📦 Building an Executable (`.exe`)

The project includes a PyInstaller specification for standalone binary builds. Run:
```cmd
build.bat
```
The compiled standalone executable will be located in the `dist/` directory.

---

## 🔒 Security & Privacy

- Sensitive configuration files (`app_config.json`), local API keys, virtual environments (`.venv`), and user documents inside `workspace/` are strictly ignored via [.gitignore](file:///e:/PRACTICE/ToolImportText/.gitignore).
- Do not commit your personal API keys when submitting pull requests or pushing commits.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
