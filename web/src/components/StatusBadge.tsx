type Tone = 'signal' | 'warning' | 'critical' | 'success' | 'dim'

export function StatusBadge({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  return <span className={`badge ${tone}`}>{children}</span>
}
