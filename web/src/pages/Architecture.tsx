export function Architecture() {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Architecture</h1>
          <p>Web UI → REST API → Algorithm Core.</p>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 24 }}>
        <h2 className="section-title">System Boundary</h2>
        <pre style={{ fontFamily: 'var(--mono)', fontSize: 12.5, color: 'var(--text-dim)', overflowX: 'auto' }}>
{`+-------------+      +----------------+      +---------------------+
|   Web UI    | ---> |   REST API      | ---> |   Algorithm Core     |
| (React/TS)  |      | (FastAPI)       |      | (pure Python DSA)    |
+-------------+      +----------------+      +---------------------+
                          |                          |
                          v                          v
                  /health, /api/v1/*        Graph, Routing, Dispatch,
                                             Events, Evacuation,
                                             Optimization, Metrics,
                                             Benchmarks`}
        </pre>
      </div>

      <div className="grid grid-2">
        <div className="panel">
          <h2 className="section-title">Data Structures</h2>
          <ul style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.9 }}>
            <li>Hash Map (EntityStore) — O(1) avg entity lookup</li>
            <li>Set — visited/uniqueness tracking</li>
            <li>Queue (deque) — BFS / event flow</li>
            <li>Binary Heap (PriorityQueue) — O(log n) dispatch/shortest path</li>
            <li>Graph (adjacency list) — city network</li>
            <li>Union-Find (DSU) — connectivity, near O(alpha(n))</li>
            <li>Tree — hierarchical district/zone aggregation</li>
          </ul>
        </div>
        <div className="panel">
          <h2 className="section-title">Algorithms</h2>
          <ul style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.9 }}>
            <li>BFS — reachability</li>
            <li>DFS — connected components</li>
            <li>Dijkstra — weighted routing (guaranteed optimal)</li>
            <li>A* — heuristic routing (optimal with admissible heuristic)</li>
            <li>Union-Find — connectivity checks</li>
            <li>Greedy / DP — resource allocation</li>
            <li>Backtracking — small constraint problems</li>
            <li>Max Flow (Edmonds-Karp) — evacuation capacity analysis</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
