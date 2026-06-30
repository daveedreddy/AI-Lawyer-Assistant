from app.services.nvidia_service import nvidia_service

response = nvidia_service.generate_response(
    query="Explain Article 21 of the Constitution of India in 5 lines.",
    context="Article 21 protects life and personal liberty."
)

print(response)