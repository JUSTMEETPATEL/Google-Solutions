/** Sidebar — session history list (WEB-01). */

import { useAppStore } from '../store/appStore';
import type { SessionSummary } from '../api/client';

const RISK_COLORS: Record<string, string> = {
  high: '#ef4444', medium: '#eab308', low: '#22c55e',
};

export function Sidebar() {
  const { sessions, selectedSessionId, setSelectedSession } = useAppStore();

  return (
    <aside style={{
      width: 280,
      minHeight: '100vh',
      background: '#1e293b',
      borderRight: '1px solid #334155',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      <div style={{ padding: '20px 16px', borderBottom: '1px solid #334155' }}>
        <h1 style={{ fontSize: 18, fontWeight: 700, color: '#3b82f6', display: 'flex', alignItems: 'center', gap: 8 }}>
          ⚖️ FairCheck
        </h1>
        <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
          AI Bias Detection Platform
        </p>
      </div>

      <div style={{ padding: '12px 16px' }}>
        <h3 style={{ fontSize: 11, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
          Sessions
        </h3>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
        {sessions.length === 0 && (
          <p style={{ padding: '12px 8px', fontSize: 13, color: '#64748b' }}>
            No scans yet. Upload a model to start.
          </p>
        )}
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelectedSession(s.id)}
            style={{
              width: '100%',
              padding: '10px 12px',
              marginBottom: 4,
              borderRadius: 8,
              border: 'none',
              background: selectedSessionId === s.id ? '#334155' : 'transparent',
              color: '#f1f5f9',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'background 0.15s',
            }}
          >
            <div style={{ fontSize: 13, fontWeight: 500 }}>{s.model_name || 'Unknown'}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
              <span style={{ fontSize: 11, color: '#94a3b8' }}>
                {s.created_at?.slice(0, 10) || '—'}
              </span>
              <span style={{
                fontSize: 10,
                fontWeight: 700,
                color: RISK_COLORS[s.risk_level?.toLowerCase()] || '#94a3b8',
                textTransform: 'uppercase',
              }}>
                {s.risk_level || '—'}
              </span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}
