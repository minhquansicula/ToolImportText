import uvicorn
import threading
import socket
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.services.upload_session_service import UploadSessionService
from src.transfer.upload_security import UploadSecurity, ImageValidationError
from src.transfer.upload_rate_limiter import UploadRateLimiter
from src.services.file_service import FileService

logger = logging.getLogger(__name__)

class LocalUploadServer:
    def __init__(self, port: int, session_service: UploadSessionService, 
                 security: UploadSecurity, rate_limiter: UploadRateLimiter,
                 file_service: FileService):
        self.port = port
        self.session_service = session_service
        self.security = security
        self.rate_limiter = rate_limiter
        self.file_service = file_service
        self.app = FastAPI()
        self._setup_routes()
        self._server = None
        self._thread = None
        self.on_upload_success = None
        
    def _get_local_ip(self) -> str:
        # Detect private local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _setup_routes(self):
        base_dir = Path(__file__).resolve().parent.parent
        
        # Mount static files
        static_dir = base_dir / "web" / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Setup templates
        templates_dir = base_dir / "web" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        templates = Jinja2Templates(directory=str(templates_dir))

        @self.app.get("/upload/{token}", response_class=HTMLResponse)
        async def get_upload_page(request: Request, token: str):
            if not self.session_service.validate_token(token):
                return HTMLResponse("<h1>Session Expired or Invalid</h1><p>Vui lòng tạo phiên mới trên máy tính.</p>", status_code=403)
            return templates.TemplateResponse(request=request, name="mobile_capture.html", context={"token": token})

        @self.app.post("/upload/{token}")
        async def upload_image(token: str, file: UploadFile = File(...)):
            if not self.session_service.validate_token(token):
                raise HTTPException(status_code=403, detail="Invalid or expired session")
                
            if not self.rate_limiter.acquire():
                raise HTTPException(status_code=429, detail="Too many requests")
                
            try:
                # File metadata validation
                content_type = file.content_type
                
                # Read file into memory (or temp file) for validation
                contents = await file.read()
                file_size = len(contents)
                self.security.validate_file_metadata(file.filename, content_type, file_size)
                
                # Generate safe filename and save to Inbox
                safe_filename = self.security.generate_safe_filename(file.filename)
                temp_path = self.file_service.inbox_dir / f"{safe_filename}.tmp"
                
                with open(temp_path, "wb") as f:
                    f.write(contents)
                    
                # Image content validation
                try:
                    self.security.validate_image_content(temp_path)
                    final_path = self.file_service.inbox_dir / safe_filename
                    temp_path.rename(final_path)
                    logger.info(f"Successfully received and validated upload: {safe_filename}")
                    if self.on_upload_success:
                        self.on_upload_success(safe_filename)
                    return JSONResponse(content={"message": "Upload thành công", "file_id": safe_filename})
                except ImageValidationError as e:
                    if temp_path.exists():
                        temp_path.unlink()
                    raise HTTPException(status_code=400, detail=str(e))

            except Exception as e:
                logger.error(f"Upload failed: {e}")
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=500, detail="Internal server error")
            finally:
                self.rate_limiter.release()

    def start(self):
        ip = self._get_local_ip()
        config = uvicorn.Config(self.app, host=ip, port=self.port, log_level="warning")
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        return f"http://{ip}:{self.port}"

    def stop(self):
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=2.0)
