from pathlib import Path
import chromadb
from chromadb.config import Settings

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database" / "chromadb"

client = chromadb.PersistentClient(
    path=str(DB_DIR),
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_collection("legal_documents")

result = collection.peek(limit=1)

print(result["metadatas"][0])