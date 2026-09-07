"""A binary-heap priority queue, implemented explicitly on top of heapq's
array operations conceptually (we implement our own sift up/down rather than
calling heapq directly) so the O(log n) push/pop behavior is ours to own,
explain, and instrument (nodes explored / operations counters)."""
from __future__ import annotations

import itertools
from typing import Generic, TypeVar

T = TypeVar("T")


class PriorityQueue(Generic[T]):
    """Min-heap priority queue with O(log n) push/pop and stable tie-breaking."""

    def __init__(self) -> None:
        self._heap: list[tuple[float, int, T]] = []
        self._counter = itertools.count()
        self.push_count = 0
        self.pop_count = 0

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def push(self, priority: float, item: T) -> None:
        entry = (priority, next(self._counter), item)
        self._heap.append(entry)
        self.push_count += 1
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from empty PriorityQueue")
        self.pop_count += 1
        last = self._heap.pop()
        if not self._heap:
            return last[2]
        top = self._heap[0]
        self._heap[0] = last
        self._sift_down(0)
        return top[2]

    def peek(self) -> T:
        return self._heap[0][2]

    def _sift_up(self, idx: int) -> None:
        heap = self._heap
        while idx > 0:
            parent = (idx - 1) // 2
            if heap[idx][0] < heap[parent][0]:
                heap[idx], heap[parent] = heap[parent], heap[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        heap = self._heap
        n = len(heap)
        while True:
            left, right = 2 * idx + 1, 2 * idx + 2
            smallest = idx
            if left < n and heap[left][0] < heap[smallest][0]:
                smallest = left
            if right < n and heap[right][0] < heap[smallest][0]:
                smallest = right
            if smallest == idx:
                break
            heap[idx], heap[smallest] = heap[smallest], heap[idx]
            idx = smallest
