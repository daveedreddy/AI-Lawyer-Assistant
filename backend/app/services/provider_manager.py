from enum import Enum


class Provider(str, Enum):
    NVIDIA = "nvidia"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OPENAI = "openai"
    LOCAL = "local"


class ProviderManager:
    """
    Controls provider priority and failover.
    """

    def __init__(self):
        self.priority = [
            Provider.NVIDIA,
            Provider.GEMINI,
            Provider.OPENROUTER,
            Provider.GROQ,
            Provider.OPENAI,
            Provider.LOCAL,
        ]

    def providers(self):
        return self.priority


provider_manager = ProviderManager()