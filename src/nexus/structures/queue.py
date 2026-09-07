"""FIFO queue (deque-backed) for BFS / event-flow processing, and a simple
hash-map-backed entity store used as the O(1) avg lookup table for city
entities (people, vehicles, incidents, stations)."""
from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Queue(Generic[T]):
    def __init__(self) -> None:
        self._items: deque[T] = deque()

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        return self._items.popleft()

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)


V = TypeVar("V")


class EntityStore(Generic[V]):
    """Hash-map-backed O(1) average lookup for entities keyed by id."""

    def __init__(self) -> None:
        self._data: dict[str, V] = {}

    def put(self, key: str, value: V) -> None:
        self._data[key] = value

    def get(self, key: str) -> V | None:
        return self._data.get(key)

    def remove(self, key: str) -> None:
        self._data.pop(key, None)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def values(self) -> Iterator[V]:
        return iter(self._data.values())

    def keys(self) -> Iterator[str]:
        return iter(self._data.keys())

    def items(self):
        return self._data.items()
