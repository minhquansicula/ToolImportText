import logging
from typing import Dict, Any
from PySide6.QtCore import QThread, Signal, QObject

from src.workers.processing_queue import ProcessingQueue
from src.models.processing_item import ProcessingStatus
from src.ocr.base_ocr_engine import BaseOCREngine
from src.extractors.base_extractor import BaseExtractor
from src.validators.document_validator import DocumentValidator
from src.ocr.image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)

class OCRWorkerSignals(QObject):
    progress_updated = Signal(str, int, str)
    processing_completed = Signal(str, object) 
    processing_failed = Signal(str, str, str) 

class OCRWorker(QThread):
    def __init__(self, queue: ProcessingQueue, ocr_engine: BaseOCREngine, 
                 extractor: BaseExtractor, validator: DocumentValidator,
                 preprocessor: ImagePreprocessor, doc_configs: Dict[str, Any]):
        super().__init__()
        self.queue = queue
        self.ocr_engine = ocr_engine
        self.extractor = extractor
        self.validator = validator
        self.preprocessor = preprocessor
        self.doc_configs = doc_configs
        self.signals = OCRWorkerSignals()
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        
    def run(self):
        logger.info("OCR Worker started.")
        while self._is_running:
            item = self.queue.get_next_item(timeout=1.0)
            if not item:
                continue
                
            if item.status != ProcessingStatus.UNPROCESSED:
                self.queue.mark_done()
                continue
                
            try:
                self.queue.update_status(item.file_id, ProcessingStatus.PROCESSING)
                self.signals.progress_updated.emit(item.file_id, 10, "Bắt đầu OCR")
                
                doc_type = "fixed_form_v1"
                config = self.doc_configs.get(doc_type, {})
                
                self.signals.progress_updated.emit(item.file_id, 30, "Đang nhận diện chữ")
                raw_results = self.ocr_engine.extract_text(item.file_path)
                
                self.signals.progress_updated.emit(item.file_id, 70, "Đang bóc tách dữ liệu")
                extracted = self.extractor.extract_fields(raw_results, config)
                
                self.signals.progress_updated.emit(item.file_id, 90, "Đang kiểm tra dữ liệu")
                doc_data = self.validator.validate_document(doc_type, extracted, config)
                
                needs_review = any(not f.manually_reviewed for f in doc_data.fields.values())
                new_status = ProcessingStatus.REVIEW_REQUIRED if needs_review else ProcessingStatus.VALID
                self.queue.update_status(item.file_id, new_status, ocr_status="Hoàn thành")
                
                self.signals.processing_completed.emit(item.file_id, doc_data)
                
            except Exception as e:
                logger.error(f"OCR failed for {item.file_id}: {e}")
                self.queue.update_status(item.file_id, ProcessingStatus.FAILED, error_summary=str(e))
                self.signals.processing_failed.emit(item.file_id, "OCR_ERROR", str(e))
            finally:
                self.queue.mark_done()
