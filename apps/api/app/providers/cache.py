from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class ProviderMemoryCache:
    """Small per-process TTL cache for provider calls.

    This keeps local development and tests from repeatedly calling the same free
    public endpoint. Phase 21C moves durable observations into PostgreSQL.
    """

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = max(ttl_seconds, 0)
        self._entries: dict[str, CacheEntry[object]] = {}

    def get(self, key: str) -> object | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at < monotonic():
            self._entries.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: object) -> None:
        if self.ttl_seconds <= 0:
            return
        self._entries[key] = CacheEntry(value=value, expires_at=monotonic() + self.ttl_seconds)

    def status(self) -> dict[str, int]:
        return {
            "entries": len(self._entries),
            "ttl_seconds": self.ttl_seconds,
        }
