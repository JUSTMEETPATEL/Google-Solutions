/** RiskScoreCard — overall risk level display (WEB-05). */

const RISK_CONFIG: Record<string, { color: string; bg: string; icon: string }> = {
  high: { color: '#ef4444', bg: 'rgba(239,68,68,0.1)', icon: '🔴' },
  medium: { color: '#eab308', bg: 'rgba(234,179,8,0.1)', icon: '🟡' },
  low: { color: '#22c55e', bg: 'rgba(34,197,94,0.1)', icon: '🟢' },
  unknown: { color: '#94a3b8', bg: 'rgba(148,163,184,0.1)', icon: '⚪' },
};

interface RiskScoreCardProps {
  level: string;
  metrics?: { pass: number; warning: number; fail: number };
}

export function RiskScoreCard({ level, metrics }: RiskScoreCardProps) {
  const config = RISK_CONFIG[level.toLowerCase()] || RISK_CONFIG.unknown;

  return (
    <div style={{
      background: config.bg,
      border: `1px solid ${config.color}33`,
      borderRadius: 12,
      padding: '20px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: 16,
    }}>
      <div style={{ fontSize: 36 }}>{config.icon}</div>
      <div>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1 }}>
          Overall Risk
        </div>
        <div style={{ fontSize: 24, fontWeight: 700, color: config.color }}>
          {level.toUpperCase()}
        </div>
        {metrics && (
          <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
            <span style={{ fontSize: 12, color: '#22c55e' }}>✓ {metrics.pass}</span>
            <span style={{ fontSize: 12, color: '#eab308' }}>⚠ {metrics.warning}</span>
            <span style={{ fontSize: 12, color: '#ef4444' }}>✗ {metrics.fail}</span>
          </div>
        )}
      </div>
    </div>
  );
}
