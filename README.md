# NEXUS

**A living city powered by Data Structures & Algorithms.**

SIMULATE · BREAK · BENCHMARK · PROVE

**Live:** https://nexus-algorithmic-city.onrender.com

> Hosted on Render's free plan, which sleeps after ~15 minutes idle — the
> first request may take 30-60s to cold-start.

NEXUS is not a generic DSA visualizer. It simulates a city — population,
vehicles, roads, incidents — where classic algorithms (graph search,
shortest path, max-flow, union-find, greedy/DP/backtracking) are the actual
mechanics driving the simulation, not decoration. Trigger a fire and watch a
real priority-queue dispatch pipeline pick a unit and route it with A*. Close
a bridge and watch max-flow evacuation analysis identify the new bottleneck.
Run chaos mode and watch the system compose multiple failures and degrade
gracefully instead of crashing.

## Quickstart

```bash
# 1. Backend
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash / macOS: source .venv/bin/activate
pip install -e ".[dev]"

python -m nexus.cli demo             # builds a city, triggers a fire, dispatches, evacuates

# 2. API server
uvicorn nexus.api.app:app --reload --port 8000
curl http://localhost:8000/health

# 3. Frontend (separate terminal)
cd web
npm install
npm run dev                          # http://localhost:5173, proxies /api and /health to :8000
```

Or run the whole thing in one container:

```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8000/health
```

## Architecture

```
+-------------+      +----------------+      +---------------------+
|   Web UI    | ---> |   REST API      | ---> |   Algorithm Core     |
| (React/TS)  |      | (FastAPI)       |      | (pure Python DSA)    |
+-------------+      +----------------+      +---------------------+
                          |                          |
                          v                          v
                  /health, /api/v1/*        Graph, Routing, Dispatch,
                                             Events, Evacuation,
                                             Optimization, Metrics,
                                             Benchmarks

Experience map:
  LAND (command center) -> SIMULATE (live city) -> TRIGGER (scenario)
    -> OBSERVE (algorithm telemetry) -> COMPARE (arena) -> PROVE (benchmark)
```

### Repository shape

```
nexus/
  src/nexus/
    structures/     Graph, Heap (PriorityQueue), UnionFind, Queue, EntityStore, Tree
    algorithms/      BFS/DFS, Dijkstra, A*, Edmonds-Karp max-flow
    optimization/    Greedy, 0/1 DP, Backtracking constraint solver
    city/            Seeded city/network generator
    events/          Fire, flood, road failure, power failure
    emergency/       5-stage dispatch pipeline
    evacuation/      Max-flow evacuation analysis
    chaos/           Composed, seeded, never-crashes chaos mode
    simulation/      Simulation engine + registry + timeline
    benchmarking/     Real benchmark runner (writes benchmarks/results/)
    metrics/         Runtime metrics store
    api/             FastAPI app (REST boundary)
    cli/             Click-based CLI (full product without the web UI)
  web/               React + TypeScript dark command-center frontend
  tests/             unit / integration / property (invariants) / scenarios
  benchmarks/results/  Real, appended JSONL benchmark records
  docs/              Complexity notes, architecture
  .github/workflows/ ci.yml (tests/lint/types), deploy.yml (ghcr image + deploy)
  Dockerfile         multi-stage: build web -> install deps -> slim runtime
  docker-compose.yml local production-like run
```

## Data structures actually doing work

| Structure | Job | Complexity |
|---|---|---|
| Hash Map (`EntityStore`) | O(1) avg entity lookup (vehicles, incidents) | O(1) avg |
| Set | visited/uniqueness tracking in traversal | O(1) avg |
| Queue (`collections.deque`) | BFS / event flow | O(1) enqueue/dequeue |
| Binary heap (`PriorityQueue`) | dispatch ordering, Dijkstra/A* frontier | O(log n) push/pop |
| Graph (adjacency list) | city road network, V/E accounting | O(1) neighbor iteration setup |
| Union-Find (DSU) | connectivity / isolated-zone detection | ~O(alpha(n)) amortized |
| Tree | hierarchical district/zone aggregation | O(depth) per op |

## Algorithms actually doing work

- **BFS** — reachability, hop-count distance
- **DFS** — connected components (chaos-mode isolated-zone detection)
- **Dijkstra** — weighted routing, always optimal
- **A\*** — heuristic routing; optimal *because* the heuristic is admissible
  (straight-line distance, and city edge weights are generated to always be
  >= straight-line distance between endpoints, degrading to 0/Dijkstra when
  coordinates are absent)
- **Union-Find** — connectivity checks
- **Greedy** — fast resource allocation heuristic
- **DP (0/1 knapsack)** — exact resource allocation on small inputs, used to
  validate the greedy heuristic
- **Backtracking** — small zone-coloring constraint problem
- **Max Flow (Edmonds-Karp)** — evacuation capacity, bottleneck, critical cut

## CLI reference

```bash
python -m nexus.cli demo
python -m nexus.cli simulate --profile medium --seed 42
python -m nexus.cli disaster --type fire --zone industrial_1
python -m nexus.cli evacuate --scenario bridge_closure
python -m nexus.cli route --from node_0 --to node_10 --algorithm astar
python -m nexus.cli benchmark --profile large
python -m nexus.cli chaos --seed 42
```

Every command supports `--help` and fails with a readable message (never a
raw stack trace) on bad input, e.g. an unknown node id.

## API reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness/readiness |
| GET | `/api/v1/city` | current city snapshot |
| POST | `/api/v1/simulations` | create a simulation (`profile`, `seed`) |
| POST | `/api/v1/simulations/{id}/events` | trigger fire/flood/road_failure/power_failure |
| GET | `/api/v1/simulations/{id}/timeline` | event history |
| GET | `/api/v1/simulations/{id}/dispatch/{incident_id}` | run the 5-stage dispatch pipeline |
| POST | `/api/v1/routes` | Dijkstra vs A* comparison for a start/goal pair |
| POST | `/api/v1/evacuation` | max-flow evacuation report |
| POST | `/api/v1/chaos` | run chaos mode against a live simulation |
| POST | `/api/v1/benchmarks` | run and persist a real benchmark |
| GET | `/api/v1/metrics` | runtime call/latency counters |

## Testing

```bash
pytest -q                       # 58 tests: unit, integration, property (invariants), scenarios
ruff check src tests            # lint
mypy src/nexus                  # type check
```

Test categories:
- **unit** — structures + algorithms: empty inputs, duplicates, disconnected graphs
- **integration** — incident -> dispatch -> arrival, road closure -> recalculation, the FastAPI surface
- **property/invariants** — path validity, flow conservation, capacity limits, across multiple seeds
- **scenarios** — chaos never crashes, seed reproducibility (city, chaos actions), evacuation scenarios

## Benchmarks

```bash
python -m nexus.cli benchmark --profile small
python -m nexus.cli benchmark --profile medium
python -m nexus.cli benchmark --profile large
python -m nexus.cli benchmark --profile stress   # capped at 50,000 nodes, see docs/complexity
```

Results are appended (never overwritten, never fabricated) to
`benchmarks/results/benchmark_results.jsonl` with profile, algorithm, seed,
runtime, nodes explored, edge relaxations, path cost, and memory.

## Docker

```bash
docker build -t nexus-algorithmic-city:local .
docker run -p 8000:8000 nexus-algorithmic-city:local
curl http://localhost:8000/health
```

or `docker compose up --build`. The image is a 3-stage build (frontend build
-> Python deps -> slim runtime), runs as a non-root user, reads config from
environment variables (see `.env.example`), and has a container `HEALTHCHECK`
against `/health`. No secrets are baked into the image.

## Deploying

`render.yaml` is a Render Blueprint for a single Docker web service (free plan,
health check on `/health`, auto-deploy on every commit to `master`). To go live:

1. Open https://render.com/deploy?repo=https://github.com/jathavedanstackup-cell/nexus-algorithmic-city
2. Sign in with GitHub and click **Apply**.

Nothing else needs configuring — no secrets or env vars are required to run.
After the first apply, each push to `master` redeploys automatically.

The container binds to the `PORT` the platform injects, so the same image runs
unchanged on Railway, Fly.io, or Cloud Run. Verified locally with `PORT=10000`:
health, static frontend, and the simulation API all respond and the container
reports `healthy`.

## Known limitations / cut for time

- Stress profile capped at 50,000 nodes (documented above), not 100,000.
- Free-plan hosting sleeps after ~15 min idle; first request cold-starts
  in 30-60s. Not a code issue — a plan characteristic.
- `docs/` beyond `docs/complexity/README.md` is intentionally thin — the
  engineering depth went into correctness, tests, and the working system
  over prose documentation.
- The Network Canvas visualization is a stylized ring layout (not a full
  force-directed graph layout) — it communicates "there is a live network"
  and highlights computed paths, but is not a literal 1:1 topology render.
