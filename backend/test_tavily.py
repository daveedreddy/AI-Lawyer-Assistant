from app.services.tavily_service import tavily_service

results = tavily_service.search(
    "What is Article 21 of the Constitution of India?"
)

print("\nFound", len(results), "results\n")

for i, item in enumerate(results, start=1):
    print("=" * 100)
    print(f"Result {i}")
    print("=" * 100)
    print("Title :", item["title"])
    print("URL   :", item["url"])
    print("Source:", item["source"])
    print()
    print(item["text"][:800])
    print("\n")