import type { DispatchTelemetry } from '../api/client'

export function TelemetryPanel({ data, loading, error }: { data?: DispatchTelemetry | null; loading?: boolean; error?: string | null }) {
  if (loading) return <div className="loading-state">Running dispatch pipeline…</div>
  if (error) return <div className="error-state">{error}</div>
  if (!data) return <div className="empty-state">Trigger an incident to see the dispatch pipeline.</div>
  return (
    <div>
      <div className="stage-list">
        {data.stage_log.map((line, i) => (
          <div className="stage-item" key={i}>{line}</div>
        ))}
      </div>
      <div className="grid grid-3" style={{ marginTop: 16 }}>
        <div className="panel metric-card">
          <div className="label">Dispatched Unit</div>
          <div className="value" style={{ fontSize: 16 }}>{data.dispatched_unit ?? 'none available'}</div>
        </div>
        <div className="panel metric-card">
          <div className="label">Route Cost</div>
          <div className="value" style={{ fontSize: 16 }}>{data.route ? data.route.cost.toFixed(2) : '—'}</div>
        </div>
        <div className="panel metric-card">
          <div className="label">Nodes Explored (total)</div>
          <div className="value" style={{ fontSize: 16 }}>{String(data.telemetry.nodes_explored_total ?? '—')}</div>
        </div>
      </div>
    </div>
  )
}
