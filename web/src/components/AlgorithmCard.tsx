import type { RouteResult } from '../api/client'
import { StatusBadge } from './StatusBadge'

export function AlgorithmCard({ name, result }: { name: string; result?: RouteResult }) {
  if (!result) {
    return (
      <div className="panel arena-col">
        <h3>{name}</h3>
        <div className="empty-state">No route computed yet.</div>
      </div>
    )
  }
  return (
    <div className="panel arena-col elevated">
      <h3 style={{ margin: 0 }}>{name}</h3>
      <StatusBadge tone={result.found ? 'success' : 'critical'}>
        {result.found ? 'path found' : 'no path'}
      </StatusBadge>
      <div>
        <div className="arena-stat"><span>Runtime</span><span>{result.runtime_ms.toFixed(2)} ms</span></div>
        <div className="arena-stat"><span>Nodes explored</span><span>{result.nodes_explored}</span></div>
        <div className="arena-stat"><span>Edge relaxations</span><span>{result.edge_relaxations}</span></div>
        <div className="arena-stat"><span>Route cost</span><span>{result.found ? result.cost.toFixed(2) : '—'}</span></div>
        <div className="arena-stat">
          <span>Optimality</span>
          <span>{result.optimal_guaranteed ? 'guaranteed (admissible h)' : 'not guaranteed'}</span>
        </div>
      </div>
    </div>
  )
}
