import logging
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "database" / "chromadb"


class RetrievalService:
    def __init__(self):
        self.model = None
        self.client = None
        self.collection = None

    def _ensure_ready(self) -> None:
        if self.model is None:
            logger.info("Loading BAAI/bge-m3 embedding model for queries.")
            self.model = SentenceTransformer("BAAI/bge-m3", device="cpu")

        if self.client is None:
            logger.info("Connecting to ChromaDB at %s.", DB_DIR)
            self.client = chromadb.PersistentClient(
                path=str(DB_DIR),
                settings=Settings(anonymized_telemetry=False),
            )

        if self.collection is None:
            self.collection = self.client.get_collection(name="legal_documents")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            self._ensure_ready()
            query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.exception("Local retrieval failed: %s", exc)
            return []

        formatted_results = []
        documents = results.get("documents") or []
        if documents and documents[0]:
            for i, text in enumerate(documents[0]):
                distance = (results.get("distances") or [[1.0]])[0][i]
                metadata = (results.get("metadatas") or [[{}]])[0][i] or {}
                formatted_results.append(
                    {
                        "text": text,
                        "metadata": metadata,
                        "score": round(1.0 - distance, 4),
                    }
                )
        return formatted_results


retrieval_service = RetrievalService()
