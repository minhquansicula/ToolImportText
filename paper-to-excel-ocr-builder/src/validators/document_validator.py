from typing import Dict, Any
from src.models.document_data import DocumentData, FieldData
from src.validators.field_validator import FieldValidator

class DocumentValidator:
    def __init__(self, field_validator: FieldValidator):
        self.field_validator = field_validator

    def validate_document(self, document_type: str, extracted_data: Dict[str, Dict[str, Any]], doc_config: Dict[str, Any], threshold: float = 0.85) -> DocumentData:
        doc_data = DocumentData(document_type=document_type)
        fields_config = doc_config.get("fields", {})
        
        for field_key, field_cfg in fields_config.items():
            ext = extracted_data.get(field_key, {"raw_value": "", "confidence": 0.0, "source": "empty"})
            raw = ext["raw_value"]
            conf = ext["confidence"]
            source = ext["source"]
            
            result = self.field_validator.validate(field_cfg, raw, conf, threshold)
            
            doc_data.fields[field_key] = FieldData(
                raw_value=raw,
                confidence=conf,
                validation_result=result,
                source=source,
                manually_reviewed=not result.requires_manual_review
            )
            
        return doc_data
