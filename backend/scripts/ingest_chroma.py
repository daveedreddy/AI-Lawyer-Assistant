import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("chroma_ingestion.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_DIR = BASE_DIR / "knowledge_base" / "processed" / "embeddings"
DB_DIR = BASE_DIR / "database" / "chromadb"

# Configuration
CONFIG = {
    "collection_name": "legal_documents",
    "batch_size": 250,
    "distance_metric": "cosine"
}

class ChromaIngestor:
    def __init__(self):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Connecting to Persistent ChromaDB at {DB_DIR}...")
        self.client = chromadb.PersistentClient(
            path=str(DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=CONFIG["collection_name"],
            metadata={"hnsw:space": CONFIG["distance_metric"]}
        )
        logger.info(f"Collection '{CONFIG['collection_name']}' is ready.")

    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """ChromaDB strictly requires scalar metadata values (str, int, float, bool)."""
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                continue
            if isinstance(value, (list, dict)):
                sanitized[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        return sanitized

    def process_all(self):
        logger.info("Starting ChromaDB Ingestion Process...")
        start_time = time.time()
        
        total_files = 0
        total_inserted = 0

        if not EMBEDDINGS_DIR.exists():
            logger.error(f"Embeddings directory not found: {EMBEDDINGS_DIR}")
            return

        for root, _, files in os.walk(EMBEDDINGS_DIR):
            for file in files:
                if not file.endswith("_embedded.json"):
                    continue

                file_path = Path(root) / file
                logger.info(f"Reading file: {file_path.name}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        records = json.load(f)

                    if not records:
                        continue

                    logger.info(f"Loaded {len(records)} embeddings from {file_path.name}")
                    
                    batch_ids, batch_embeddings, batch_texts, batch_metadatas = [], [], [], []

                    for record in records:
                        batch_ids.append(record["id"])
                        batch_embeddings.append(record["embedding"])
                        batch_texts.append(record["text"])
                        batch_metadatas.append(self.sanitize_metadata(record.get("metadata", {})))

                    # Batch Insertion
                    batch_size = CONFIG["batch_size"]
                    for i in range(0, len(batch_ids), batch_size):
                        end_idx = i + batch_size
                        
                        # Upsert prevents duplicates. If ID exists, it updates. If not, it inserts.
                        self.collection.upsert(
                            ids=batch_ids[i:end_idx],
                            embeddings=batch_embeddings[i:end_idx],
                            documents=batch_texts[i:end_idx],
                            metadatas=batch_metadatas[i:end_idx]
                        )
                        logger.info(f"Inserted batch {int(i/batch_size) + 1} ({len(batch_ids[i:end_idx])} records) for {file}")

                    total_inserted += len(batch_ids)
                    total_files += 1

                except Exception as e:
                    logger.error(f"Failed to ingest {file}: {e}")

        # Final Verification Phase
        exec_time = round(time.time() - start_time, 2)
        total_in_db = self.collection.count()
        
        logger.info("========== INGESTION VERIFICATION ==========")
        logger.info(f"Collection Name  : {CONFIG['collection_name']}")
        logger.info(f"Files Processed  : {total_files}")
        logger.info(f"Total Embeddings : {total_in_db}")
        logger.info(f"Execution Time   : {exec_time} seconds")
        logger.info("Status           : SUCCESSFUL")
        logger.info("============================================")

if __name__ == "__main__":
    ingestor = ChromaIngestor()
    ingestor.process_all()