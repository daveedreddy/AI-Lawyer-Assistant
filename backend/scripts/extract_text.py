import os
import json
import csv
import logging
import hashlib
from pathlib import Path
import fitz  # PyMuPDF

# Initialize Logging Configuration for Enterprise Systems
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("extraction_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "knowledge_base" / "raw"
PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed" / "extracted"
MANIFEST_FILE = PROCESSED_DIR / "manifest.json"

class DocumentExtractor:
    """
    Lightweight, automated text extraction engine.
    Dedicated solely to file reading, basic OS metadata attachment, 
    and state tracking via a processing manifest.
    """
    def __init__(self):
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()

    def load_manifest(self):
        """Loads the processing manifest to track file states and prevent redundant processing."""
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        """Persists the updated manifest tracking state to storage."""
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save manifest file: {e}")

    def get_file_hash(self, file_path):
        """Generates a unique SHA-256 hash for state comparison and change verification."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def extract_pdf(self, file_path):
        """Extracts plain text layer from standard PDF structures."""
        text = ""
        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted:
                logger.warning(f"Encryption detected. Skipping password-protected PDF: {file_path.name}")
                return None
                
            for page in doc:
                text += page.get_text("text") + "\n"
            return text.strip()
        except fitz.FileDataError:
            logger.error(f"Corrupted format exception. Skipping file: {file_path.name}")
            return None
        except Exception as e:
            logger.error(f"Unexpected parsing exception on PDF {file_path.name}: {e}")
            return None

    def extract_json(self, file_path):
        """Normalizes and structures raw JSON documents into readable context."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Parsing exception on JSON {file_path.name}: {e}")
            return None

    def extract_csv(self, file_path):
        """Converts tabular structures into standardized narrative string streams."""
        text = ""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    text += " | ".join(row) + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Parsing exception on CSV {file_path.name}: {e}")
            return None

    def extract_txt(self, file_path):
        """Reads flat unformatted document structures directly."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Parsing exception on TXT {file_path.name}: {e}")
            return None

    def process_all(self):
        """Orchestrates recursive scan operations across the target raw repository."""
        logger.info("Initializing lightweight document extraction routine...")
        processed_count, skipped_count, failed_count = 0, 0, 0

        # Mappings configuration for system extensibility
        extractors = {
            ".pdf": self.extract_pdf,
            ".json": self.extract_json,
            ".csv": self.extract_csv,
            ".txt": self.extract_txt
        }

        for root, _, files in os.walk(RAW_DIR):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                if ext not in extractors:
                    continue  # Safely bypass unsupported extensions

                relative_path = file_path.relative_to(RAW_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)
                
                # Check manifest to skip unaltered records
                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    logger.info(f"Skipped (No changes detected): {relative_path}")
                    skipped_count += 1
                    continue

                logger.info(f"Processing ingestion target: {relative_path}")
                extracted_text = extractors[ext](file_path)

                if extracted_text:
                    # Construct basic OS-level metadata structure only
                    metadata = {
                        "source_filename": file_path.name,
                        "relative_path": str_relative_path,
                        "source_folder": str(relative_path.parent),
                        "file_extension": ext,
                        "content": extracted_text
                    }

                    # Maintain identical hierarchy patterns inside destination folder
                    output_folder = PROCESSED_DIR / relative_path.parent
                    output_folder.mkdir(parents=True, exist_ok=True)

                    output_filename = file_path.stem + f"_{ext[1:]}_extracted.json"
                    output_filepath = output_folder / output_filename

                    try:
                        with open(output_filepath, "w", encoding="utf-8") as out_f:
                            json.dump(metadata, out_f, indent=4, ensure_ascii=False)
                        
                        # Update tracking system on success status
                        self.manifest[str_relative_path] = current_hash
                        processed_count += 1
                        logger.info(f"Success: Stored payload at {output_filepath.relative_to(BASE_DIR)}")
                    except Exception as e:
                        logger.error(f"Storage write operation failed for {output_filename}: {e}")
                        failed_count += 1
                else:
                    failed_count += 1

        self.save_manifest()
        logger.info(f"Routine complete. Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count}")

if __name__ == "__main__":
    extractor = DocumentExtractor()
    extractor.process_all()