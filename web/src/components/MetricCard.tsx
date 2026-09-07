interface Props {
  label: string
  value?: string | number | null
  sub?: string
  loading?: boolean
  error?: string | null
}

export function MetricCard({ label, value, sub, loading, error }: Props) {
  const stateClass = error ? 'error' : loading ? 'loading' : ''
  return (
    <div className={`panel metric-card ${stateClass}`}>
      <div className="label">{label}</div>
      <div className="value">
        {error ? 'error' : loading ? '…' : value ?? '—'}
      </div>
      {sub && !error && <div className="sub">{sub}</div>}
      {error && <div className="sub">{error}</div>}
    </div>
  )
}
