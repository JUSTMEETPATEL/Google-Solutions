/** OversightForm — human oversight log form (WEB-07). */

import { useState } from 'react';
import { submitOversight } from '../api/client';

interface OversightFormProps {
  sessionId: string;
}

export function OversightForm({ sessionId }: OversightFormProps) {
  const [reviewer, setReviewer] = useState('');
  const [decision, setDecision] = useState('approved');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitOversight(sessionId, {
        reviewer,
        date: new Date().toISOString().slice(0, 10),
        decision,
        notes: notes || undefined,
      });
      setSubmitted(true);
    } catch {
      // silently ignore
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div style={{
        background: 'rgba(34,197,94,0.08)',
        border: '1px solid #22c55e33',
        borderRadius: 12,
        padding: 20,
        textAlign: 'center',
      }}>
        <div style={{ fontSize: 28, marginBottom: 8 }}>✅</div>
        <p style={{ fontSize: 14, color: '#22c55e', fontWeight: 600 }}>
          Oversight decision recorded
        </p>
        <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
          {reviewer} — {decision} — {new Date().toISOString().slice(0, 10)}
        </p>
      </div>
    );
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    background: '#0f172a',
    border: '1px solid #334155',
    borderRadius: 8,
    padding: '10px 12px',
    color: '#f1f5f9',
    fontSize: 13,
    outline: 'none',
  };

  return (
    <form onSubmit={handleSubmit} style={{
      background: '#1e293b',
      borderRadius: 12,
      padding: 20,
    }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9', marginBottom: 16 }}>
        👤 Human Oversight
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div>
          <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>
            Reviewer Name *
          </label>
          <input
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="Dr. Jane Smith"
            required
            style={inputStyle}
          />
        </div>

        <div>
          <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>
            Decision
          </label>
          <select
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            style={{ ...inputStyle, cursor: 'pointer' }}
          >
            <option value="approved">✅ Approved — Model is fair for deployment</option>
            <option value="conditional">⚠️ Conditional — Requires mitigation before deployment</option>
            <option value="rejected">❌ Rejected — Model shows unacceptable bias</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>
            Notes (optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Additional observations..."
            rows={3}
            style={{ ...inputStyle, resize: 'vertical' }}
          />
        </div>

        <button
          type="submit"
          disabled={!reviewer || submitting}
          style={{
            padding: '10px 0',
            borderRadius: 8,
            border: 'none',
            background: reviewer ? '#3b82f6' : '#334155',
            color: '#fff',
            fontSize: 14,
            fontWeight: 600,
            cursor: reviewer ? 'pointer' : 'not-allowed',
          }}
        >
          {submitting ? 'Submitting...' : 'Record Decision'}
        </button>
      </div>
    </form>
  );
}
