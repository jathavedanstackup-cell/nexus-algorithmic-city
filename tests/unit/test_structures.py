import pytest

from nexus.structures.graph import Graph
from nexus.structures.heap import PriorityQueue
from nexus.structures.queue import EntityStore, Queue
from nexus.structures.tree import Tree
from nexus.structures.union_find import UnionFind


def test_graph_empty():
    g = Graph()
    assert g.num_nodes == 0
    assert g.num_edges == 0
    assert list(g.neighbors("missing")) == []


def test_graph_add_and_close_edge():
    g = Graph()
    g.add_edge("a", "b", weight=2.0, capacity=5)
    assert g.num_nodes == 2
    assert g.num_edges == 1
    neighbors = list(g.neighbors("a"))
    assert neighbors[0].to == "b"
    assert g.set_edge_active("a", "b", False)
    assert list(g.neighbors("a")) == []
    assert next(iter(g.neighbors("a", only_active=False))).active is False


def test_graph_duplicate_edges_allowed_as_multigraph_like():
    g = Graph()
    g.add_edge("a", "b", weight=1)
    g.add_edge("a", "b", weight=3)
    assert len(list(g.neighbors("a"))) == 2


def test_priority_queue_orders_by_priority():
    pq = PriorityQueue()
    pq.push(5, "e")
    pq.push(1, "a")
    pq.push(3, "c")
    assert pq.pop() == "a"
    assert pq.pop() == "c"
    assert pq.pop() == "e"
    assert pq.is_empty()


def test_priority_queue_empty_pop_raises():
    pq = PriorityQueue()
    with pytest.raises(IndexError):
        pq.pop()


def test_union_find_basic():
    uf = UnionFind()
    uf.union("a", "b")
    uf.union("b", "c")
    assert uf.connected("a", "c")
    assert not uf.connected("a", "z")
    assert len(uf.components()) == 2  # {a,b,c} and {z}


def test_queue_fifo():
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    assert q.dequeue() == 1
    assert q.dequeue() == 2
    assert q.is_empty()


def test_entity_store_lookup():
    store = EntityStore()
    store.put("x", {"v": 1})
    assert store.get("x") == {"v": 1}
    assert store.get("missing") is None
    store.remove("x")
    assert "x" not in store


def test_tree_aggregate():
    t = Tree("city", {"pop": 0})
    t.add("city", "district_a", {"pop": 100})
    t.add("city", "district_b", {"pop": 200})
    assert t.aggregate("city", "pop") == 300
