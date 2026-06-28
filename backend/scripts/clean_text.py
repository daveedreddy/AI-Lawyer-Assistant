import os
import re
import json
import logging
import hashlib
from pathlib import Path

# Initialize Logging Configuration for Enterprise Systems
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cleaning_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = BASE_DIR / "knowledge_base" / "processed" / "extracted"
CLEANED_DIR = BASE_DIR / "knowledge_base" / "processed" / "cleaned"
MANIFEST_FILE = CLEANED_DIR / "cleaner_manifest.json"

class TextCleaner:
    """
    Automated text sanitization engine.
    Reads extracted JSON payloads, removes formatting noise, 
    and outputs clean JSON payloads ready for chunking.
    """
    def __init__(self):
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()

    def load_manifest(self):
        """Loads the processing manifest for the cleaner pipeline."""
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read cleaner manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        """Persists the cleaner manifest to storage."""
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save cleaner manifest file: {e}")

    def get_file_hash(self, file_path):
        """Generates a SHA-256 hash for the extracted JSON to detect upstream changes."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def sanitize_text(self, text):
        """
        Applies Regex heuristics to remove legal document noise.
        - Removes page numbers (e.g., Page 1, Page 1 of 20)
        - Removes repeating line artifacts
        - Normalizes multiple spaces and newlines
        """
        if not text:
            return ""

        # 1. Remove Page Numbers (e.g., "Page 4", "- 4 -", "Page 2 of 10")
        text = re.sub(r'(?i)\bpage\s+\d+\b(\s+of\s+\d+)?', '', text)
        text = re.sub(r'\n\s*-\s*\d+\s*-\s*\n', '\n', text)
        
        # 2. Fix broken words across lines (e.g., "juris-\ndiction" -> "jurisdiction")
        text = re.sub(r'([a-zA-Z]+)-\n([a-zA-Z]+)', r'\1\2', text)
        
        # 3. Remove excessive newlines (more than 2 becomes exactly 2 for paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 4. Remove excessive horizontal whitespaces or tabs
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def process_all(self):
        """Scans extracted JSONs, cleans content, and routes to cleaned directory."""
        logger.info("Initializing automated text cleaning routine...")
        processed_count, skipped_count, failed_count = 0, 0, 0

        for root, _, files in os.walk(EXTRACTED_DIR):
            for file in files:
                if not file.endswith(".json") or file == "manifest.json":
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(EXTRACTED_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)

                # Skip if already cleaned and source hasn't changed
                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    skipped_count += 1
                    continue

                logger.info(f"Sanitizing payload: {relative_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)

                    # Execute cleaning heuristic on the content
                    raw_content = payload.get("content", "")
                    cleaned_content = self.sanitize_text(raw_content)
                    
                    # Update payload
                    payload["content"] = cleaned_content
                    payload["processing_stage"] = "cleaned"

                    # Construct output path preserving hierarchy
                    output_folder = CLEANED_DIR / relative_path.parent
                    output_folder.mkdir(parents=True, exist_ok=True)
                    output_filepath = output_folder / file.replace("_extracted.json", "_cleaned.json")

                    with open(output_filepath, "w", encoding="utf-8") as out_f:
                        json.dump(payload, out_f, indent=4, ensure_ascii=False)

                    self.manifest[str_relative_path] = current_hash
                    processed_count += 1
                    logger.info(f"Success: Cleaned payload stored at {output_filepath.relative_to(BASE_DIR)}")

                except Exception as e:
                    logger.error(f"Failed to process {file.name}: {e}")
                    failed_count += 1

        self.save_manifest()
        logger.info(f"Routine complete. Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count}")

if __name__ == "__main__":
    cleaner = TextCleaner()
    cleaner.process_all()