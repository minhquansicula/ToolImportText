import logging
from pathlib import Path
from typing import List, Any
import json

from src.models.ocr_result import OCRResult, BoundingBox
from src.ocr.base_ocr_engine import BaseOCREngine

logger = logging.getLogger(__name__)

class CloudOCREngine(BaseOCREngine):
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "gemini")
        raw_key = config.get("api_key", "").strip()
        if not raw_key or raw_key == "YOUR_API_KEY_HERE":
            import os
            raw_key = os.environ.get("OPENROUTER_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        self.api_key = raw_key
        self.model_name = config.get("model_name", "gemini-1.5-flash")
        
    def initialize(self) -> None:
        if not self.api_key:
            raise RuntimeError("API Key is missing for Cloud OCR Engine. Vui lòng thiết lập trong Cài đặt.")
            
    def extract_text(self, image_path: Path | str) -> List[OCRResult]:
        if not self.api_key:
            self.initialize()
            
        try:
            if self.provider.lower() == "gemini":
                return self._extract_gemini(image_path)
            elif self.provider.lower() == "openrouter":
                return self._extract_openrouter(image_path)
            else:
                raise ValueError(f"Unsupported cloud provider: {self.provider}")
        except Exception as e:
            logger.error(f"Cloud OCR extraction failed: {e}")
            raise RuntimeError(f"Lỗi truy xuất AI: {e}")

    def _extract_gemini(self, image_path: Path | str) -> List[OCRResult]:
        from google import genai
        
        client = genai.Client(api_key=self.api_key)
        
        with open(str(image_path), "rb") as f:
            image_data = f.read()
            
        ext = Path(image_path).suffix.lower()
        mime_type = "image/jpeg"
        if ext == ".png": mime_type = "image/png"
        elif ext == ".webp": mime_type = "image/webp"
        
        prompt = """Bạn là chuyên gia OCR tiếng Việt. 
Hãy đọc toàn bộ nội dung văn bản trong hình ảnh đính kèm một cách chính xác nhất.
Kết quả phải được trả về dưới định dạng JSON là một DANH SÁCH (Array) chứa các chuỗi (String).
Mỗi dòng văn bản trong hình ảnh tương ứng với một chuỗi trong danh sách JSON đó.

Ví dụ:
[
  "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
  "Độc lập - Tự do - Hạnh phúc"
]"""
        
        # In modern google-genai, we should use Part.from_bytes
        contents = [
            genai.types.Part.from_bytes(data=image_data, mime_type=mime_type),
            prompt
        ]
        
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            
            lines = json.loads(response.text)
            
            results = []
            dummy_box = BoundingBox(points=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
            
            if isinstance(lines, list):
                for i, text in enumerate(lines):
                    results.append(OCRResult(
                        text=str(text),
                        confidence=1.0,
                        bounding_box=dummy_box,
                        sequence_number=i,
                        source_image=str(image_path)
                    ))
            elif isinstance(lines, dict):
                # Fallback if model wraps it in an object
                for i, (k, v) in enumerate(lines.items()):
                    results.append(OCRResult(
                        text=f"{v}",
                        confidence=1.0,
                        bounding_box=dummy_box,
                        sequence_number=i,
                        source_image=str(image_path)
                    ))
            else:
                raise ValueError("AI trả về JSON không đúng định dạng mảng (Array).")
                
            return results
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise e

    # Fallback model list for OpenRouter — only models that support image input
    # Ordered by: cost-effective first, then quality
    OPENROUTER_FALLBACK_MODELS = [
        "google/gemini-3.5-flash",          # Fast, cheap, vision
        "google/gemini-3.8-flash",          # Latest Gemini Flash, vision
        "qwen/qwen3.8-flash",              # Free-tier friendly, vision
        "z-ai/glm-5.3-flash",             # Vision support
        "anthropic/claude-fable-5.1",      # High quality, vision
        "google/gemini-2.5-flash",         # Older but stable, vision
    ]

    def _extract_openrouter(self, image_path: Path | str) -> List[OCRResult]:
        import base64
        import urllib.request
        import urllib.error
        import io
        from PIL import Image
        
        # Resize and compress image to reduce payload and save credits
        img = Image.open(str(image_path))
        
        # Resize if larger than 1600px on longest side (plenty for OCR)
        max_side = 1600
        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logger.info(f"Resized image from {Image.open(str(image_path)).size} to {new_size}")
        
        # Convert to RGB if necessary (e.g. RGBA PNGs)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Compress to JPEG in memory
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80, optimize=True)
        image_data = buffer.getvalue()
        mime_type = "image/jpeg"
        
        logger.info(f"Compressed image size: {len(image_data) / 1024:.0f} KB")
        
        base64_image = base64.b64encode(image_data).decode("utf-8")
        image_url = f"data:{mime_type};base64,{base64_image}"
        
        prompt = """You are an expert OCR reader for Vietnamese documents.
Read ALL text from the attached image accurately.

RULES:
1. Preserve EXACT line order as shown on the paper, top to bottom, left to right.
2. Merge text on the SAME visual line into ONE string (e.g. "Name: Nguyen Van A    Gender: Male" → one string).
3. Keep original formatting: uppercase, punctuation, spaces, special characters.
4. Do NOT reorder, add, remove, or translate any content.
5. Output the Vietnamese text exactly as printed.

Return ONLY a JSON array of strings, no other text.

Example:
[
  "BỆNH VIỆN ĐA KHOA ABC",
  "123 Nguyễn Huệ, TP. Hồ Chí Minh",
  "ĐƠN THUỐC",
  "Họ và tên: NGUYỄN VĂN A    Giới tính: Nam"
]"""


        # Build model list: configured model first, then fallbacks
        models_to_try = []
        configured_model = self.model_name if self.model_name else self.OPENROUTER_FALLBACK_MODELS[0]
        models_to_try.append(configured_model)
        for m in self.OPENROUTER_FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model_id in models_to_try:
            logger.info(f"Trying OpenRouter model: {model_id}")
            
            payload = {
                "model": model_id,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.0,
                "max_tokens": 2000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8265",
                "X-Title": "Paper to Excel OCR",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    
                content = resp_data["choices"][0]["message"]["content"]
                
                # Clean markdown formatting if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                lines = json.loads(content)
                
                results = []
                dummy_box = BoundingBox(points=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
                
                if isinstance(lines, list):
                    for i, text in enumerate(lines):
                        results.append(OCRResult(
                            text=str(text),
                            confidence=1.0,
                            bounding_box=dummy_box,
                            sequence_number=i,
                            source_image=str(image_path)
                        ))
                elif isinstance(lines, dict):
                    for i, (k, v) in enumerate(lines.items()):
                        results.append(OCRResult(
                            text=f"{v}",
                            confidence=1.0,
                            bounding_box=dummy_box,
                            sequence_number=i,
                            source_image=str(image_path)
                        ))
                else:
                    raise ValueError("AI trả về JSON không đúng định dạng mảng (Array).")
                
                logger.info(f"OpenRouter OCR success with model: {model_id}")
                return results
                
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                logger.warning(f"OpenRouter model {model_id} failed ({e.code}): {error_body}")
                last_error = f"Model {model_id}: HTTP {e.code} - {error_body}"
                # Retry with next model for client/rate/payment errors
                if e.code in (400, 402, 404, 429, 503):
                    continue
                # For other errors (401 auth, etc.), don't retry
                raise RuntimeError(f"OpenRouter API Error: {e.code} - {error_body}")
            except Exception as e:
                logger.warning(f"OpenRouter model {model_id} error: {e}")
                last_error = str(e)
                continue
        
        # All models failed
        raise RuntimeError(f"Tất cả model OpenRouter đều thất bại. Lỗi cuối: {last_error}")

