import { useState } from 'react'
import { AlgorithmCard } from '../components/AlgorithmCard'
import { NetworkCanvas } from '../components/NetworkCanvas'
import { useSimulation } from '../SimulationContext'
import { api } from '../api/client'
import type { RouteCompare } from '../api/client'

export function Arena() {
  const { simId, city } = useSimulation()
  const [start, setStart] = useState('node_0')
  const [goal, setGoal] = useState('node_1')
  const [result, setResult] = useState<RouteCompare | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function compare() {
    if (!simId) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.postRoute(simId, start, goal)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Algorithm Arena</h1>
          <p>Same input, different algorithms — measured honestly, side by side.</p>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 24 }}>
        <div className="controls-row">
          <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Start node</label>
          <input value={start} onChange={(e) => setStart(e.target.value)} placeholder="node_0" />
          <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Goal node</label>
          <input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="node_1" />
          <button className="btn primary" onClick={compare} disabled={!simId || loading}>
            {loading ? 'COMPUTING…' : 'COMPARE ROUTES'}
          </button>
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-faint)' }}>
          City has {city?.num_nodes ?? '—'} nodes (node_0 .. node_{city ? city.num_nodes - 1 : '?'}).
        </p>
        {error && <div className="error-state">{error}</div>}
        {result && !result.dijkstra.found && (
          <div className="error-state">No path exists between these nodes in the current network.</div>
        )}
        {result && result.dijkstra.found && result.astar.found && (
          <div className="badge success" style={{ marginTop: 8 }}>
            {result.agree_on_cost ? 'Both algorithms agree on optimal cost' : 'Cost mismatch detected'}
          </div>
        )}
      </div>

      <div className="grid grid-2" style={{ marginBottom: 24 }}>
        <AlgorithmCard name="Dijkstra" result={result?.dijkstra} />
        <AlgorithmCard name="A* (admissible heuristic)" result={result?.astar} />
      </div>

      <div className="panel">
        <h2 className="section-title">Route Visualization (A*)</h2>
        <NetworkCanvas nodeCount={city?.num_nodes ?? 0} highlightPath={result?.astar.path} />
      </div>
    </div>
  )
}
