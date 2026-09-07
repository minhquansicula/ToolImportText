import re
from pathlib import Path

skill_path = Path("e:/PRACTICE/ToolImportText/paper-to-excel-ocr-builder/SKILL.md")
content = skill_path.read_text(encoding="utf-8")

# 1. Update Name and Description
content = content.replace(
    "name: paper-to-excel-ocr-builder\n",
    "name: paper-to-text-ocr-assistant\n"
)
content = content.replace(
    "description: Design, implement, review, test, and package a local Windows desktop application that receives document photos from a phone over the local network, extracts printed data using PaddleOCR and OpenCV, allows human review and validation, and safely writes approved values into Excel using openpyxl.",
    "description: Design, implement, review, test, and package a local Windows desktop application that receives document photos from a phone over the local network, extracts printed data using PaddleOCR and OpenCV, allows human review, and exports OCR results as TXT, CSV, JSON, or TSV for manual pasting into Excel."
)
content = content.replace("# Paper to Excel OCR — Builder Skill", "# Paper to Text OCR Assistant — Builder Skill")

# 2. Future Phase addition
future_phase = """
---

## Future Phase: Excel Automation (Not in MVP)

In a future phase, the application will add automated Excel integration:
- Row matching against existing Excel records using configurable matching keys.
- Cell-state classification (missing, already complete, conflict).
- Change preview with proposed actions per field before any Excel modification.
- Missing-cell completion with openpyxl — backup, atomic save, correct data types, leading-zero preservation.
- Conflict display without automatic overwrite.
- Stale-data protection.
- Merged-cell and formula-cell safety.
"""
if "## Future Phase:" not in content:
    content += future_phase

skill_path.write_text(content, encoding="utf-8")
