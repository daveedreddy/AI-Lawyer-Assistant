import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Locate backend/database/chromadb correctly from backend/app/services/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "database" / "chromadb"

class RetrievalService:
    def __init__(self):
        logger.info("Loading BAAI/bge-m3 embedding model for queries...")
        self.model = SentenceTransformer("BAAI/bge-m3", device="cpu")
        
        logger.info(f"Connecting to ChromaDB at {DB_DIR}...")
        self.client = chromadb.PersistentClient(path=str(DB_DIR), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_collection(name="legal_documents")
        logger.info("Retrieval Service initialized successfully.")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Generates query embedding, hits ChromaDB, and returns structured result blocks.
        """
        # 1. Generate Query Embedding
        query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()
        
        # 2. Similarity Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # 3. Format Output
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(1.0 - results["distances"][0][i], 4) # Distance to similarity score
                })
        return formatted_results

# Global Instance for clean imports
retrieval_service = RetrievalService()