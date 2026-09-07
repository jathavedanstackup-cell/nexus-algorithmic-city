"""Disjoint Set Union (Union-Find) with path compression + union by rank.
Near O(alpha(n)) amortized per operation. Used for connectivity checks
(isolated-zone detection in chaos mode, component counting)."""
from __future__ import annotations


class UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}

    def make_set(self, x: str) -> None:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0

    def find(self, x: str) -> str:
        self.make_set(x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        # path compression
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self._rank[ra] < self._rank[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        if self._rank[ra] == self._rank[rb]:
            self._rank[ra] += 1
        return True

    def connected(self, a: str, b: str) -> bool:
        return self.find(a) == self.find(b)

    def components(self) -> dict[str, set[str]]:
        groups: dict[str, set[str]] = {}
        for node in self._parent:
            root = self.find(node)
            groups.setdefault(root, set()).add(node)
        return groups
