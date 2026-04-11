/** RegulationSelector — dropdown for regulation framework (WEB-04). */

const REGULATIONS = [
  { value: 'eu_ai_act_high', label: 'EU AI Act (High Risk)' },
  { value: 'eu_ai_act_limited', label: 'EU AI Act (Limited Risk)' },
  { value: 'india_dpdpa', label: 'India DPDPA' },
  { value: 'custom', label: 'Custom' },
];

interface RegulationSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function RegulationSelector({ value, onChange }: RegulationSelectorProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <label style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8', whiteSpace: 'nowrap' }}>
        Regulation:
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          background: '#1e293b',
          color: '#f1f5f9',
          border: '1px solid #334155',
          borderRadius: 8,
          padding: '8px 12px',
          fontSize: 13,
          cursor: 'pointer',
          outline: 'none',
        }}
      >
        {REGULATIONS.map((r) => (
          <option key={r.value} value={r.value}>{r.label}</option>
        ))}
      </select>
    </div>
  );
}
