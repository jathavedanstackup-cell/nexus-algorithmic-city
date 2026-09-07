"""A simple hierarchical tree used for indexed/organizational city data,
e.g. District -> Zone -> Facility hierarchy for fast hierarchical lookups
and aggregation (population roll-ups per district)."""
from __future__ import annotations

from collections.abc import Iterator


class TreeNode:
    __slots__ = ("children", "data", "id", "parent")

    def __init__(self, node_id: str, data: dict | None = None) -> None:
        self.id = node_id
        self.data = data or {}
        self.children: list[TreeNode] = []
        self.parent: TreeNode | None = None

    def add_child(self, child: TreeNode) -> None:
        child.parent = self
        self.children.append(child)


class Tree:
    def __init__(self, root_id: str, data: dict | None = None) -> None:
        self.root = TreeNode(root_id, data)
        self._index: dict[str, TreeNode] = {root_id: self.root}

    def add(self, parent_id: str, node_id: str, data: dict | None = None) -> TreeNode:
        parent = self._index[parent_id]
        node = TreeNode(node_id, data)
        parent.add_child(node)
        self._index[node_id] = node
        return node

    def get(self, node_id: str) -> TreeNode | None:
        return self._index.get(node_id)

    def walk(self) -> Iterator[TreeNode]:
        stack = [self.root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(node.children)

    def aggregate(self, node_id: str, field: str) -> float:
        """Sum `field` over a node's entire subtree."""
        node = self._index[node_id]
        total = 0.0
        stack = [node]
        while stack:
            n = stack.pop()
            total += n.data.get(field, 0)
            stack.extend(n.children)
        return total
