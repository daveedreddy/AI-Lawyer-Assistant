from pathlib import Path
import json

path = Path("knowledge_base/processed/metadata/constution/indian constitution part-1_pdf_metadata.json")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(json.dumps(data[0], indent=2, ensure_ascii=False))