import type { TimelineEvent } from '../api/client'

export function EventTimeline({ events, loading, error }: { events: TimelineEvent[]; loading?: boolean; error?: string | null }) {
  if (loading) return <div className="loading-state">Loading timeline…</div>
  if (error) return <div className="error-state">{error}</div>
  if (!events.length) return <div className="empty-state">No events yet. Trigger a scenario to populate the timeline.</div>
  return (
    <div className="timeline">
      {[...events].reverse().map((e) => (
        <div className="timeline-item" key={e.id}>
          <span className="t">{new Date(e.timestamp).toLocaleTimeString()}</span>
          <span>{e.description}</span>
        </div>
      ))}
    </div>
  )
}
