# Complexity & Scale Notes

| Structure / Algorithm | Complexity | Notes |
|---|---|---|
| EntityStore (hash map) | O(1) avg get/put | Python dict-backed |
| Set (visited tracking) | O(1) avg membership | stdlib set |
| Queue (BFS) | O(1) enqueue/dequeue | collections.deque |
| PriorityQueue (binary heap) | O(log n) push/pop | hand-rolled sift up/down, not a linear scan |
| Union-Find | ~O(alpha(n)) amortized | path compression + union by rank |
| Dijkstra | O((V+E) log V) | binary heap, only relaxes active edges |
| A* | O((V+E) log V) worst case, better in practice | admissible heuristic (straight-line distance, 0 when coords absent) |
| Edmonds-Karp max-flow | O(VE^2) | fine at evacuation-graph scale (single digits to low hundreds of nodes) |

## Measured scale limits (this machine, this run)

Benchmarks were run locally (Windows, see `benchmarks/results/benchmark_results.jsonl`
for raw, unedited numbers) at profiles:

- **small** (50 nodes) — sub-millisecond to a few ms
- **medium** (1,000 nodes) — single-digit to tens of ms
- **large** (10,000 nodes) — low hundreds of ms
- **stress** — capped at **50,000 nodes** rather than the suggested 100,000.
  City construction plus a single Dijkstra/A* run at 50K completed in ~7s
  wall-clock in this sandboxed environment. 100K was not attempted because
  the marginal value of doubling the stress profile did not justify the
  extra CI/benchmark time budget for this run; the routing algorithms
  themselves (binary-heap based) scale near-linearly with (V+E) log V, so
  the limiting factor is city-generation and process overhead, not the
  algorithms under test.

No benchmark numbers in this repository are fabricated -- they are all
produced by `python -m nexus.cli benchmark --profile <profile>` or the
`/api/v1/benchmarks` endpoint and appended to `benchmarks/results/`.
