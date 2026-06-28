import os
import json
import logging
import hashlib
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("chunking_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "knowledge_base" / "processed" / "cleaned"
CHUNKED_DIR = BASE_DIR / "knowledge_base" / "processed" / "chunks"
MANIFEST_FILE = CHUNKED_DIR / "chunker_manifest.json"

class DocumentChunker:
    """
    Intelligent semantic text splitting engine.
    Routes chunking strategies: CSVs (row grouping) vs PDFs/TXTs (Recursive splitting).
    """
    def __init__(self, chunk_size=1200, chunk_overlap=200, rows_per_chunk=15):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.rows_per_chunk = rows_per_chunk
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        CHUNKED_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()

    def load_manifest(self):
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read chunker manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save chunker manifest file: {e}")

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def process_all(self):
        logger.info("Initializing Chunking Pipeline...")
        processed_count, skipped_count, failed_count = 0, 0, 0

        if not CLEANED_DIR.exists():
            logger.error(f"Source directory {CLEANED_DIR} not found. Ensure clean_text.py has been run.")
            return

        for root, _, files in os.walk(CLEANED_DIR):
            for file in files:
                if not file.endswith(".json") or "manifest" in file.lower():
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(CLEANED_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)

                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    skipped_count += 1
                    continue

                logger.info(f"Processing: {file}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)

                    raw_content = payload.get("content", "")
                    if not raw_content:
                        logger.warning(f"Empty content in {file}, skipping.")
                        continue

                    file_ext = payload.get("file_extension", "").lower()
                    
                    # Processing Strategy
                    if file_ext == ".csv":
                        lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
                        if len(lines) > 1:
                            header = lines[0]
                            data_rows = lines[1:]
                            text_chunks = []
                            for i in range(0, len(data_rows), self.rows_per_chunk):
                                batch = data_rows[i : i + self.rows_per_chunk]
                                text_chunks.append(f"COLUMNS: {header}\nRECORDS:\n" + "\n".join(batch))
                        else:
                            text_chunks = lines
                    else:
                        text_chunks = self.text_splitter.split_text(raw_content)
                    
                    chunked_payload = {
                        "source_filename": payload.get("source_filename"),
                        "relative_path": payload.get("relative_path"),
                        "source_folder": payload.get("source_folder"),
                        "file_extension": payload.get("file_extension"),
                        "processing_stage": "chunked",
                        "total_chunks": len(text_chunks),
                        "chunks": []
                    }

                    for index, chunk_text in enumerate(text_chunks):
                        chunked_payload["chunks"].append({
                            "chunk_index": index,
                            "text": chunk_text,
                            "char_count": len(chunk_text)
                        })

                    output_folder = CHUNKED_DIR / relative_path.parent
                    output_folder.mkdir(parents=True, exist_ok=True)
                    output_filepath = output_folder / file.replace("_cleaned.json", "_chunked.json")

                    with open(output_filepath, "w", encoding="utf-8") as out_f:
                        json.dump(chunked_payload, out_f, indent=4, ensure_ascii=False)

                    self.manifest[str_relative_path] = current_hash
                    processed_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to process {file}: {e}")
                    failed_count += 1

        self.save_manifest()
        logger.info(f"Done. Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count}")

if __name__ == "__main__":
    chunker = DocumentChunker(chunk_size=1200, chunk_overlap=200, rows_per_chunk=15)
    chunker.process_all()