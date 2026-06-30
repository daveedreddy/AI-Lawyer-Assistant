import json
from app.services.retrieval_service import retrieval_service
from app.services.nvidia_service import nvidia_service


def run_test():
    query = "What is Article 21?"
    print(f"\n[Step 1] Running query retrieval for: '{query}'")

    matched_docs = retrieval_service.search(query, top_k=2)

    context_blocks = []
    for doc in matched_docs:
        context_blocks.append(f"Document Text: {doc['text']}\nMetadata: {json.dumps(doc['metadata'])}")

    combined_context = "\n\n---\n\n".join(context_blocks)
    print(f"Retrieved {len(matched_docs)} context chunks successfully.")

    print("\n[Step 2] Sending query and context to the NVIDIA model...")
    answer = nvidia_service.generate_response(query, combined_context)

    print("\n================== NVIDIA GENERATED ANSWER ==================")
    print(answer)
    print("============================================================")


if __name__ == "__main__":
    run_test()