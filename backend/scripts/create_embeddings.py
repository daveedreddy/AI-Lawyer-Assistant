import os
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure sentence-transformers is installed: pip install sentence-transformers torch
from sentence_transformers import SentenceTransformer

# Initialize Logging Configuration for Enterprise Systems
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("embeddings_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "knowledge_base" / "processed" / "metadata"
EMBEDDINGS_DIR = BASE_DIR / "knowledge_base" / "processed" / "embeddings"
MANIFEST_FILE = EMBEDDINGS_DIR / "embedding_manifest.json"

# Centralized Configuration for Embeddings
EMBEDDING_CONFIG = {
    "model_name": "BAAI/bge-m3",  # Swapped to BGE-M3 for Multilingual & Indian Language Support
    "batch_size": 32,
    "device": "cpu",  # Change to "cuda" or "mps" for GPU acceleration
    "max_seq_length": 8192, # BGE-M3 natively supports long contexts up to 8192 tokens
    "normalize_embeddings": True,
    "expected_dimension": 1024 # BGE-M3 defaults to 1024 dimensions
}


class JSONStorageDriver:
    """
    Encapsulated storage driver handling file system persistence.
    Isolating this allows seamless transition to Parquet, NumPy, or Direct DB ingestion later.
    """
    @staticmethod
    def save(output_filepath: Path, records: List[Dict[str, Any]]) -> None:
        """Saves vector records locally using a highly compressed JSON format."""
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filepath, "w", encoding="utf-8") as out_f:
            json.dump(records, out_f, separators=(',', ':'), ensure_ascii=False)


class EmbeddingsGenerator:
    """
    Dedicated semantic embedding generator optimized for production scale.
    Vectorizes enriched chunks, enforces deterministic hashing for unique vector IDs,
    validates output dimensions, and isolates the persistence layer for architectural scalability.
    """
    def __init__(self, config: Dict[str, Any], storage_driver=JSONStorageDriver):
        self.config = config
        self.storage_driver = storage_driver
        
        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()
        
        logger.info(f"Loading embedding model: {self.config['model_name']} on {self.config['device'].upper()}...")
        self.model = SentenceTransformer(self.config["model_name"], device=self.config["device"])
        
        if hasattr(self.model, "max_seq_length"):
            self.model.max_seq_length = self.config["max_seq_length"]
            
        logger.info("Model loaded successfully.")

    def load_manifest(self) -> Dict[str, str]:
        """Loads the processing manifest for the embeddings pipeline."""
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read embedding manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        """Persists the embedding manifest to storage."""
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save embedding manifest file: {e}")

    def get_file_hash(self, file_path: Path) -> str:
        """Generates a SHA-256 hash for the enriched metadata JSON."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def generate_deterministic_id(self, relative_path: str, chunk_index: int) -> str:
        """Generates a unique, stable, reproducible chunk ID using a SHA-256 hash."""
        seed_string = f"{relative_path}_chunk_{chunk_index}"
        return hashlib.sha256(seed_string.encode("utf-8")).hexdigest()

    def build_semantic_representation(self, chunk: Dict[str, Any]) -> str:
        """Constructs a dense semantic string optimized for vectorization."""
        metadata = chunk.get("metadata", {})
        context_parts = []

        doc_type = metadata.get("document_type")
        if doc_type:
            context_parts.append(f"Document Type: {doc_type}")

        act_name = metadata.get("act_name")
        if act_name:
            context_parts.append(f"Act Name: {act_name}")
            
        court_name = metadata.get("court_name")
        if court_name:
            context_parts.append(f"Court: {court_name}")

        case_title = metadata.get("case_title")
        if case_title:
            context_parts.append(f"Case: {case_title}")

        for entity in ["part", "chapter", "section", "article", "rule", "schedule", "clause", "order"]:
            val = metadata.get(entity)
            if val and isinstance(val, list):
                context_parts.append(f"{entity.capitalize()}: {', '.join(val)}")

        keywords = metadata.get("keywords", [])
        if keywords:
            context_parts.append(f"Keywords: {', '.join(keywords)}")

        context_header = " | ".join(context_parts)
        chunk_text = chunk.get("text", "")
        
        if context_header:
            return f"{context_header}\n\nContent:\n{chunk_text}"
        return chunk_text

    def process_all(self):
        """Orchestrates batch vectorization across all metadata-enriched documents."""
        logger.info("Initializing Stable Multilingual Embeddings Generation Pipeline...")
        start_time = time.time()
        
        processed_count, skipped_count, failed_count, total_chunks_embedded = 0, 0, 0, 0

        for root, _, files in os.walk(METADATA_DIR):
            for file in files:
                if not file.endswith(".json") or "manifest" in file.lower():
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
                        enriched_chunks = json.load(f)

                    if not isinstance(enriched_chunks, list):
                        logger.warning(f"Unexpected payload structure in {file}. Expected a list of chunks.")
                        failed_count += 1
                        continue

                    semantic_texts = [self.build_semantic_representation(chunk) for chunk in enriched_chunks]
                    
                    if not semantic_texts:
                        logger.warning(f"No valid text found in {file}. Skipping.")
                        continue

                    # Execute Batch Encoding using Sentence Transformers
                    embeddings = self.model.encode(
                        semantic_texts, 
                        batch_size=self.config["batch_size"],
                        normalize_embeddings=self.config["normalize_embeddings"],
                        show_progress_bar=False,
                        convert_to_numpy=True
                    )

                    vector_records = []
                    expected_dim = self.config["expected_dimension"]

                    for index, (chunk, embedding) in enumerate(zip(enriched_chunks, embeddings)):
                        actual_dim = embedding.shape[0]
                        
                        # Guardrail: Verify embedding output dimensions match configuration limits
                        if actual_dim != expected_dim:
                            logger.error(
                                f"Dimension mismatch in {file} at chunk index {index}. "
                                f"Expected {expected_dim}, got {actual_dim}. Skipping this chunk record."
                            )
                            continue

                        # Generate deterministic ID to guarantee idempotency across pipeline execution cycles
                        stable_id = self.generate_deterministic_id(str_relative_path, index)

                        vector_records.append({
                            "id": stable_id,
                            "text": chunk.get("text"),
                            "embedding": embedding.tolist(),
                            "metadata": chunk.get("metadata", {})
                        })

                    # Persist records using the abstract storage driver
                    output_filepath = EMBEDDINGS_DIR / relative_path.parent / file.replace("_metadata.json", "_embedded.json")
                    self.storage_driver.save(output_filepath, vector_records)

                    self.manifest[str_relative_path] = current_hash
                    processed_count += 1
                    total_chunks_embedded += len(vector_records)
                    logger.info(f"Success: Embedded {len(vector_records)} stable vectors for {file}")

                except Exception as e:
                    logger.error(f"Failed to process {file}: {e}")
                    failed_count += 1

        self.save_manifest()
        
        execution_time = round(time.time() - start_time, 2)
        logger.info(
            f"Embeddings Pipeline Complete in {execution_time}s. "
            f"Files Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count} | "
            f"Total Vectors Generated: {total_chunks_embedded}"
        )


if __name__ == "__main__":
    generator = EmbeddingsGenerator(EMBEDDING_CONFIG)
    generator.process_all()