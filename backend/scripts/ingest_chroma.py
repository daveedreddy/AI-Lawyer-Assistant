import os
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure chromadb is installed: pip install chromadb
import chromadb
from chromadb.config import Settings

# Initialize Logging Configuration for Enterprise Systems
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("chromadb_ingestion.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_DIR = BASE_DIR / "knowledge_base" / "processed" / "embeddings"

# Centralized Configuration for ChromaDB
CHROMA_CONFIG = {
    "database_path": str(BASE_DIR / "database" / "chromadb"), # Database path is now fully configurable
    "collection_name": "legal_documents",
    "batch_size": 250,
    "distance_metric": "cosine",
    "expected_dimension": 1024 # BGE-M3 outputs 1024-dimensional vectors
}


class ChromaIngestor:
    """
    Dedicated database ingestion module.
    Reads pre-generated vector embeddings, validates sequence constraints,
    and executes highly efficient, idempotent upsert operations into Persistent ChromaDB.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Resolve database and manifest paths dynamically from configuration
        self.db_path = Path(self.config["database_path"])
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.db_path / "ingestion_manifest.json"
        
        self.manifest = self.load_manifest()
        
        logger.info(f"Initializing Persistent ChromaDB Client at {self.db_path}...")
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Re-use or Create Collection with the specified distance metric
        logger.info(f"Connecting to collection: '{self.config['collection_name']}'...")
        self.collection = self.client.get_or_create_collection(
            name=self.config["collection_name"],
            metadata={"hnsw:space": self.config["distance_metric"]}
        )
        logger.info("ChromaDB Client and Collection initialized successfully.")

    def load_manifest(self) -> Dict[str, str]:
        """Loads the processing manifest for the ingestion pipeline."""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read ingestion manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        """Persists the ingestion manifest to storage."""
        try:
            with open(self.manifest_file, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save ingestion manifest file: {e}")

    def get_file_hash(self, file_path: Path) -> str:
        """Generates a SHA-256 hash for the embedding JSON to detect upstream changes."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares metadata strictly for ChromaDB.
        ChromaDB rejects None/null values and complex nested lists/dicts.
        This function safely converts arrays into strings and drops null keys.
        """
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                continue  # Skip nulls, ChromaDB does not accept them
            
            if isinstance(value, (list, dict)):
                sanitized[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        return sanitized

    def process_all(self):
        """Orchestrates the reading of embedding files and routes them into ChromaDB via upserts."""
        logger.info("Initializing ChromaDB Batch Ingestion Pipeline (Upsert Strategy)...")
        start_time = time.time()
        
        files_processed, files_skipped, files_failed = 0, 0, 0
        total_vectors_upserted, total_vectors_failed = 0, 0

        for root, _, files in os.walk(EMBEDDINGS_DIR):
            for file in files:
                if not file.endswith(".json") or "manifest" in file.lower():
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(EMBEDDINGS_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)

                # Skip unchanged embedding files
                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    files_skipped += 1
                    continue

                logger.info(f"Ingesting payload: {relative_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        vector_records = json.load(f)

                    if not isinstance(vector_records, list):
                        logger.warning(f"Unexpected payload structure in {file}. Skipping.")
                        files_failed += 1
                        continue

                    # Arrays to hold current file's valid data
                    batch_ids = []
                    batch_embeddings = []
                    batch_documents = []
                    batch_metadatas = []

                    expected_dim = self.config["expected_dimension"]

                    # 1. Prepare, Validate and Sanitize Data
                    for record in vector_records:
                        embedding = record.get("embedding", [])
                        actual_dim = len(embedding)
                        
                        # Guardrail: Verify embedding length matches configuration limits before database push
                        if actual_dim != expected_dim:
                            logger.error(
                                f"Dimension mismatch in vector record '{record.get('id', 'unknown')}' from file {file}. "
                                f"Expected {expected_dim}, got {actual_dim}. Skipping this vector entry."
                            )
                            total_vectors_failed += 1
                            continue

                        batch_ids.append(record["id"])
                        batch_embeddings.append(embedding)
                        batch_documents.append(record["text"])
                        batch_metadatas.append(self.sanitize_metadata(record.get("metadata", {})))

                    # 2. Execute Batch Upserts (Safely overwrite or insert records atomically)
                    if batch_ids:
                        batch_size = self.config["batch_size"]
                        for i in range(0, len(batch_ids), batch_size):
                            end_idx = i + batch_size
                            
                            # Using collection.upsert instead of add to maintain clean, repeatable state updates
                            self.collection.upsert(
                                ids=batch_ids[i:end_idx],
                                embeddings=batch_embeddings[i:end_idx],
                                documents=batch_documents[i:end_idx],
                                metadatas=batch_metadatas[i:end_idx]
                            )
                        total_vectors_upserted += len(batch_ids)

                    self.manifest[str_relative_path] = current_hash
                    files_processed += 1
                    logger.info(f"Success: Upserted {len(batch_ids)} vectors for {file}")

                except Exception as e:
                    logger.error(f"Failed to ingest {file}: {e}")
                    files_failed += 1

        self.save_manifest()
        
        execution_time = round(time.time() - start_time, 2)
        logger.info(
            f"ChromaDB Ingestion Complete in {execution_time}s.\n"
            f"Files Processed: {files_processed} | Skipped: {files_skipped} | Failed: {files_failed}\n"
            f"Total Vectors Safely Ingested/Updated: {total_vectors_upserted}\n"
            f"Total Defective Vectors Dropped: {total_vectors_failed}"
        )


if __name__ == "__main__":
    ingestor = ChromaIngestor(CHROMA_CONFIG)
    ingestor.process_all()