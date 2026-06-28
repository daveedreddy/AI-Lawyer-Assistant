import os
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure sentence-transformers is installed: pip install sentence-transformers
from sentence_transformers import SentenceTransformer

# Initialize Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("embedding_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "knowledge_base" / "processed" / "metadata"
EMBEDDINGS_DIR = BASE_DIR / "knowledge_base" / "processed" / "embeddings"
MANIFEST_FILE = EMBEDDINGS_DIR / "embedding_manifest.json"

# Restored Multilingual Configuration for BGE-M3
EMBEDDING_CONFIG = {
    "model_name": "BAAI/bge-m3",
    "batch_size": 16,                        
    "device": "cpu",                         
    "max_seq_length": 8192,                  
    "normalize_embeddings": True,
    "expected_dimension": 1024               
}

class EmbeddingGenerator:
    """
    Vector Generation Engine.
    Loads BAAI/bge-m3 locally, processes JSON array chunks, builds semantic context,
    and generates 1024-dimensional dense vector embeddings.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        logger.info(f"Loading Embedding Model: '{self.config['model_name']}' on {self.config['device']}...")
        start_time = time.time()
        
        self.model = SentenceTransformer(self.config["model_name"], device=self.config["device"])
        
        if hasattr(self.model, "max_seq_length"):
            self.model.max_seq_length = self.config["max_seq_length"]
            
        logger.info(f"Model loaded successfully in {round(time.time() - start_time, 2)} seconds.")
        
        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()

    def load_manifest(self) -> Dict[str, str]:
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read embedding manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save embedding manifest file: {e}")

    def get_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def build_semantic_representation(self, chunk: Dict[str, Any]) -> str:
        """Constructs a dense semantic string optimized for vectorization."""
        metadata = chunk.get("metadata", {})
        context_parts = []

        for entity in ["document_type", "act_name", "court_name", "case_title"]:
            val = metadata.get(entity)
            if val:
                context_parts.append(f"{entity.replace('_', ' ').title()}: {val}")

        for entity in ["part", "chapter", "section", "article", "rule", "schedule"]:
            val = metadata.get(entity)
            if val and isinstance(val, list):
                context_parts.append(f"{entity.capitalize()}: {', '.join(val)}")

        context_header = " | ".join(context_parts)
        chunk_text = chunk.get("text", "")
        
        if context_header:
            return f"{context_header}\n\nContent:\n{chunk_text}"
        return chunk_text

    def process_all(self):
        logger.info("Starting Batch Vectorization Pipeline...")
        
        if not METADATA_DIR.exists():
            logger.error(f"Source metadata directory {METADATA_DIR} not found.")
            return

        processed_count, skipped_count, failed_count = 0, 0, 0

        for root, _, files in os.walk(METADATA_DIR):
            for file in files:
                # STRICT FILTER: Ignore stray files, only process proper metadata outputs
                if not file.endswith("_metadata.json") or "manifest" in file.lower():
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(METADATA_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)

                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    skipped_count += 1
                    continue

                logger.info(f"Vectorizing payload: {relative_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)

                    # FIX: Safely handle the JSON Array structure produced by generate_metadata.py
                    if isinstance(payload, list):
                        chunks = payload
                    else:
                        logger.warning(f"Unexpected JSON structure in {file}. Expected a list of chunks.")
                        failed_count += 1
                        continue

                    if not chunks:
                        logger.warning(f"No chunks found in {file}. Skipping.")
                        continue

                    # Construct context-rich strings for the embedding model
                    texts_to_embed = [self.build_semantic_representation(chunk) for chunk in chunks]
                    
                    embeddings = self.model.encode(
                        texts_to_embed,
                        batch_size=self.config["batch_size"],
                        show_progress_bar=False,
                        normalize_embeddings=self.config["normalize_embeddings"]
                    )

                    embedding_records = []
                    for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                        
                        if len(vector) != self.config["expected_dimension"]:
                            raise ValueError(f"Dimension mismatch! Expected {self.config['expected_dimension']}, got {len(vector)}")

                        # Use the pre-existing ID from metadata, or fallback to a deterministic hash
                        chunk_id = chunk.get("chunk_id")
                        if not chunk_id:
                            chunk_id = f"doc_{hashlib.md5(f'{str_relative_path}_{index}'.encode()).hexdigest()}"

                        embedding_records.append({
                            "id": chunk_id,
                            "embedding": vector.tolist(),
                            "text": chunk.get("text", ""),
                            "metadata": chunk.get("metadata", {})
                        })

                    output_folder = EMBEDDINGS_DIR / relative_path.parent
                    output_folder.mkdir(parents=True, exist_ok=True)
                    output_filepath = output_folder / file.replace("_metadata.json", "_embedded.json")

                    with open(output_filepath, "w", encoding="utf-8") as out_f:
                        json.dump(embedding_records, out_f, separators=(',', ':'), ensure_ascii=False)

                    self.manifest[str_relative_path] = current_hash
                    processed_count += 1
                    logger.info(f"Success: Generated {len(embedding_records)} embeddings for {file}")

                except Exception as e:
                    logger.error(f"Failed to generate embeddings for {file}: {e}")
                    failed_count += 1

        self.save_manifest()
        logger.info(f"Embedding generation complete. Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count}")


if __name__ == "__main__":
    generator = EmbeddingGenerator(EMBEDDING_CONFIG)
    generator.process_all()