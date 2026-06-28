import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database" / "chromadb"

app = FastAPI(title="AI Lawyer - Retrieval Test API")

# Initialize models and DB on startup
class RetrieverService:
    def __init__(self):
        logger.info("Loading BAAI/bge-m3 embedding model for queries...")
        # Device is set to cpu to match your embedding pipeline
        self.model = SentenceTransformer("BAAI/bge-m3", device="cpu")
        
        logger.info("Connecting to ChromaDB...")
        self.client = chromadb.PersistentClient(path=str(DB_DIR), settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_collection(name="legal_documents")
        logger.info("Retriever Service Ready.")

    def search(self, query: str, top_k: int = 5):
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
                    "score": 1.0 - results["distances"][0][i] # Convert distance to similarity score
                })
        return formatted_results

# Initialize service globally
retriever = RetrieverService()

# Request Schema
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/retrieve")
async def retrieve_documents(request: QueryRequest):
    try:
        results = retriever.search(request.query, request.top_k)
        return results
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the testing server
    uvicorn.run(app, host="0.0.0.0", port=8000)