import time
from typing import Any, Dict, Optional


class CacheService:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return entry["value"]

    def set(self, key: str, value: Any) -> None:
        self._store[key] = {"value": value, "timestamp": time.time()}

    def clear(self) -> None:
        self._store.clear()


cache_service = CacheService()
