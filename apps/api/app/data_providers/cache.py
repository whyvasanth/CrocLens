from dataclasses import dataclass
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class InMemoryTTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None:
            return None

        if entry.expires_at < monotonic():
            self._entries.pop(key, None)
            return None

        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._entries[key] = CacheEntry(value=value, expires_at=monotonic() + self.ttl_seconds)

    def last_retrieved_keys(self) -> list[str]:
        return sorted(self._entries)
