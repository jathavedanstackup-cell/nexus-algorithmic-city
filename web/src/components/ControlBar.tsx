interface Props {
  profile: string
  seed: number
  onProfileChange: (p: string) => void
  onSeedChange: (s: number) => void
  onRebuild: () => void
  busy?: boolean
}

const PROFILES = ['small', 'medium', 'large', 'stress']

export function ControlBar({ profile, seed, onProfileChange, onSeedChange, onRebuild, busy }: Props) {
  return (
    <div className="controls-row">
      <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Profile</label>
      <select value={profile} onChange={(e) => onProfileChange(e.target.value)} disabled={busy}>
        {PROFILES.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      <label style={{ fontSize: 12, color: 'var(--text-dim)' }}>Seed</label>
      <input
        type="number"
        value={seed}
        onChange={(e) => onSeedChange(Number(e.target.value))}
        disabled={busy}
        style={{ width: 90 }}
      />
      <button className="btn" onClick={onRebuild} disabled={busy}>
        {busy ? 'BUILDING…' : 'REBUILD CITY'}
      </button>
    </div>
  )
}
