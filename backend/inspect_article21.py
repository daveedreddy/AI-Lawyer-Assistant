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

results = collection.query(
    query_texts=["Article 21"],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

for i in range(len(results["documents"][0])):
    print("=" * 80)
    print("Distance:", results["distances"][0][i])
    print("Metadata:", results["metadatas"][0][i])
    print("Document:")
    print(results["documents"][0][i][:600])