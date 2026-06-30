from app.orchestrator.query_orchestrator import query_orchestrator

query = "What is Article 21?"

response = query_orchestrator.process_query(
    query=query,
    top_k=3
)

print("\n" + "=" * 80)
print("QUERY")
print("=" * 80)
print(response.query)

print("\n" + "=" * 80)
print("ANSWER")
print("=" * 80)
print(response.answer)

print("\n" + "=" * 80)
print("RETRIEVED DOCUMENTS")
print("=" * 80)

for i, doc in enumerate(response.retrieved_documents, start=1):
    print(f"\nResult {i}")
    print(f"Score    : {doc.score:.4f}")
    print(f"Metadata : {doc.metadata}")
    print("-" * 80)
    print(doc.text[:400])