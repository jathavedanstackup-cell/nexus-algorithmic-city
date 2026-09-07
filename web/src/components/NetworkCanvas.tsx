import { useMemo } from 'react'

interface Props {
  nodeCount: number
  highlightPath?: string[]
  loading?: boolean
}

// Renders a stylized, deterministic representation of the city graph: a ring
// of nodes sized by nodeCount, with an optional highlighted path drawn as an
// arc through a subset of them. This is a lightweight visual anchor, not a
// full force-directed layout -- it communicates "there is a live network"
// without pretending to show the literal topology.
export function NetworkCanvas({ nodeCount, highlightPath, loading }: Props) {
  const points = useMemo(() => {
    const n = Math.min(nodeCount || 24, 60)
    const pts: { x: number; y: number }[] = []
    for (let i = 0; i < n; i++) {
      const angle = (i / n) * Math.PI * 2
      const r = 120 + (i % 3) * 20
      pts.push({ x: 160 + r * Math.cos(angle), y: 140 + r * Math.sin(angle) * 0.7 })
    }
    return pts
  }, [nodeCount])

  if (loading) return <div className="network-canvas loading-state">Loading network…</div>
  if (!nodeCount) return <div className="network-canvas empty-state">No simulation loaded.</div>

  const highlightCount = highlightPath ? Math.min(highlightPath.length, points.length) : 0

  return (
    <svg className="network-canvas" viewBox="0 0 320 280" xmlns="http://www.w3.org/2000/svg">
      {points.map((p, i) => {
        const next = points[(i + 1) % points.length]
        return (
          <line
            key={`e${i}`}
            x1={p.x} y1={p.y} x2={next.x} y2={next.y}
            stroke="#1f2733" strokeWidth={1}
          />
        )
      })}
      {highlightCount > 1 &&
        Array.from({ length: highlightCount - 1 }).map((_, i) => (
          <line
            key={`h${i}`}
            x1={points[i].x} y1={points[i].y}
            x2={points[i + 1].x} y2={points[i + 1].y}
            stroke="#3fd0ff" strokeWidth={2.5}
            style={{ filter: 'drop-shadow(0 0 4px rgba(63,208,255,0.8))' }}
          />
        ))}
      {points.map((p, i) => (
        <circle
          key={`n${i}`}
          cx={p.x} cy={p.y} r={i < highlightCount ? 4 : 2.5}
          fill={i < highlightCount ? '#3fd0ff' : '#8996a6'}
        />
      ))}
    </svg>
  )
}
