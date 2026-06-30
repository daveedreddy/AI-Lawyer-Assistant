import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


class Settings:
    APP_NAME = "AI Lawyer Assistant"
    APP_VERSION = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # NVIDIA / LLM
    NVIDIA_API_KEY: str | None = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

    # Tavily
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

    # RAG
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    MAX_QUERY_LENGTH: int = int(os.getenv("MAX_QUERY_LENGTH", "2000"))

    # Supabase
    SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str | None = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_JWT_SECRET: str | None = os.getenv("SUPABASE_JWT_SECRET")

    # Storage
    STORAGE_BUCKET_DOCUMENTS: str = os.getenv("STORAGE_BUCKET_DOCUMENTS", "legal-documents")

    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

    @property
    def supabase_ready(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)


settings = Settings()
