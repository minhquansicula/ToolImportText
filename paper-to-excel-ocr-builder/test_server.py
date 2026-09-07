import time
from pathlib import Path
import logging

from src.services.upload_session_service import UploadSessionService
from src.transfer.upload_security import UploadSecurity
from src.transfer.upload_rate_limiter import UploadRateLimiter
from src.services.file_service import FileService
from src.transfer.local_upload_server import LocalUploadServer

logging.basicConfig(level=logging.INFO)

def run_test_server():
    print("Khởi tạo dịch vụ...")
    workspace = Path("./workspace")
    file_service = FileService(workspace)
    session_service = UploadSessionService()
    
    security = UploadSecurity(
        allowed_extensions=[".jpg", ".png", ".webp", ".jpeg"],
        allowed_mime_types=["image/jpeg", "image/png", "image/webp"],
        max_size_mb=15,
        max_width=8000,
        max_height=8000,
        max_pixel_count=40000000
    )
    rate_limiter = UploadRateLimiter()

    server = LocalUploadServer(
        port=8265,
        session_service=session_service,
        security=security,
        rate_limiter=rate_limiter,
        file_service=file_service
    )

    url = server.start()
    session = session_service.create_session()
    
    print("\n" + "="*50)
    print(f"Máy chủ đã chạy tại: {url}")
    print(f"Mở đường link sau trên điện thoại của bạn (cùng mạng Wi-Fi):")
    print(f"{url}/upload/{session.token}")
    print("="*50 + "\n")
    print("Nhấn Ctrl+C để dừng máy chủ...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang dừng máy chủ...")
        server.stop()
        print("Đã dừng.")

if __name__ == "__main__":
    run_test_server()
