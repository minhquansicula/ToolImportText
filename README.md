# 📄 Paper to Text OCR Assistant

Phần mềm chuyển đổi tài liệu giấy/hình ảnh thành văn bản kỹ thuật số hỗ trợ xuất dữ liệu ra nhiều định dạng (TXT, CSV, JSON), tích hợp tải ảnh trực tiếp từ điện thoại qua mạng nội bộ bằng mã QR và hỗ trợ AI OCR đa dạng (PaddleOCR Offline & Cloud AI: OpenRouter/Gemini).

---

## ✨ Tính năng nổi bật

- **🔍 Nhận diện OCR linh hoạt:**
  - **AI Cục bộ (Offline):** Sử dụng PaddleOCR chạy trực tiếp trên máy tính mà không cần Internet hay tốn chi phí API.
  - **AI Đám mây (Cloud AI):** Tích hợp OpenRouter / Gemini API với các mô hình thị giác tiên tiến (Gemini 2.5 Flash, 1.5 Pro,...) giúp đọc chính xác tiếng Việt cả khi chữ viết tay hoặc ảnh chụp mờ, nghiêng.
- **📱 Tải ảnh nhanh bằng điện thoại (Mobile Upload):**
  - Tích hợp máy chủ mini nội bộ (FastAPI) tạo mã QR code.
  - Người dùng quét QR bằng camera điện thoại để chụp và tải ảnh thẳng vào ứng dụng trên máy tính mà không cần cắm cáp hay gửi qua Zalo/Facebook (giữ nguyên chất lượng ảnh gốc).
- **📋 Xem & Chỉnh sửa kết quả trực quan:**
  - Giao diện trực quan chia 3 cột: Danh sách ảnh tải lên, Trình xem ảnh phóng to/thu nhỏ, và Bảng xem nội dung OCR.
  - Cho phép chỉnh sửa từng dòng văn bản sau khi nhận diện.
- **💾 Đa dạng định dạng xuất:**
  - Xuất file văn bản thô: `.txt`
  - Xuất bảng biểu: `.csv`
  - Xuất cấu trúc dữ liệu: `.json`

---

## 📂 Cấu trúc dự án

```text
ToolImportText/
├── .gitignore
├── README.md
└── paper-to-excel-ocr-builder/
    ├── app.py                      # File khởi chạy ứng dụng chính (PySide6)
    ├── build.bat                   # Script đóng gói file chạy .exe bằng PyInstaller
    ├── requirements.txt            # Danh sách thư viện cần cài đặt
    ├── config/
    │   ├── app_config.example.json # File cấu hình mẫu (không chứa API key)
    │   └── document_type_fixed.json
    ├── src/
    │   ├── ocr/                    # Bộ máy OCR (PaddleOCR, Cloud AI OpenRouter/Gemini)
    │   ├── services/               # Quản lý file, export, session, qr code
    │   ├── transfer/               # Local server, bảo mật & giới hạn tải file từ mobile
    │   ├── ui/                     # Giao diện người dùng đồ họa (PySide6)
    │   ├── validators/             # Bộ kiểm tra và chuẩn hóa dữ liệu
    │   └── web/                    # Giao diện web chụp/tải ảnh cho điện thoại
    └── workspace/                  # Thư mục lưu trữ ảnh và dữ liệu làm việc (được ignore)
```

---

## 🚀 Hướng dẫn cài đặt & Chạy ứng dụng

### 1. Yêu cầu hệ thống
- Hệ điều hành: Windows 10/11
- Python: Phiên bản 3.10 hoặc 3.11 (khuyến nghị)

### 2. Cài đặt môi trường
1. Clone repository về máy:
   ```bash
   git clone https://github.com/minhquansicula/ToolImportText.git
   cd ToolImportText/paper-to-excel-ocr-builder
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   pip install PySide6 openpyxl
   ```
   *(Nếu bạn muốn dùng động cơ PaddleOCR cục bộ, cài thêm `paddlepaddle` và `paddleocr`)*.

### 3. Thiết lập cấu hình (API Key)
1. Trong thư mục `paper-to-excel-ocr-builder/config/`, copy file `app_config.example.json` thành `app_config.json`:
   ```powershell
   copy config\app_config.example.json config\app_config.json
   ```

2. Cung cấp API Key bằng **một trong hai cách**:
   - **Cách 1 (Khuyên dùng):** Mở ứng dụng, bấm nút **"Cài đặt"** trên thanh công cụ và dán API Key vào ô nhập.
   - **Cách 2:** Đặt biến môi trường trên hệ thống:
     ```powershell
     $env:OPENROUTER_API_KEY="your_key_here"
     # hoặc
     $env:GEMINI_API_KEY="your_key_here"
     ```

### 4. Khởi chạy ứng dụng
Chạy trực tiếp file `app.py`:
```bash
python app.py
```

---

## 📦 Đóng gói file chạy `.exe`

Dự án đã có sẵn cấu hình PyInstaller spec. Để build thành file `.exe`:
```cmd
build.bat
```
File thực thi sau khi build sẽ nằm trong thư mục `dist/`.

---

## 🔒 Bảo mật

- Dự án đã cấu hình [.gitignore](file:///e:/PRACTICE/ToolImportText/.gitignore) để không bao giờ theo dõi file `app_config.json`, tài khoản, key cá nhân hoặc hình ảnh cá nhân trong thư mục `workspace/`.
- Khi đóng góp mã nguồn (commit), vui lòng kiểm tra để không để lộ API Key vào code.
