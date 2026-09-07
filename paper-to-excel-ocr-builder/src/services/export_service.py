import json
import csv
from pathlib import Path
from typing import Dict, Any

class ExportService:
    @staticmethod
    def export_txt(data: Dict[str, Any], output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            for k, v in data.items():
                f.write(f"{k}: {v['raw_value']}\n")
                
    @staticmethod
    def export_csv(data: Dict[str, Any], output_path: Path):
        with open(output_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            writer.writerow([v["raw_value"] for v in data.values()])
            
    @staticmethod
    def export_tsv(data: Dict[str, Any], output_path: Path):
        with open(output_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(data.keys())
            writer.writerow([v["raw_value"] for v in data.values()])
            
    @staticmethod
    def export_json(data: Dict[str, Any], output_path: Path):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
