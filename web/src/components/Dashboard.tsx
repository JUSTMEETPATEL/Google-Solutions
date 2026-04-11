/** Dashboard — main view assembling all components. */

import { useEffect, useState } from 'react';
import { BiasCharts } from './BiasCharts';
import { RiskScoreCard } from './RiskScoreCard';
import { RegulationSelector } from './RegulationSelector';
import { OversightForm } from './OversightForm';
import { PDFExport } from './PDFExport';
import { FileUpload } from './FileUpload';
import { useAppStore } from '../store/appStore';
import { fetchSession } from '../api/client';

export function Dashboard() {
  const { selectedSessionId, regulation, setRegulation } = useAppStore();
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedSessionId) {
      setSession(null);
      return;
    }
    setLoading(true);
    fetchSession(selectedSessionId)
      .then((data) => setSession(data))
      .catch(() => setSession(null))
      .finally(() => setLoading(false));
  }, [selectedSessionId]);

  // No session selected — show upload view
  if (!selectedSessionId) {
    return (
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <FileUpload />
      </main>
    );
  }

  if (loading) {
    return (
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: '#94a3b8', fontSize: 16 }}>⏳ Loading session...</p>
      </main>
    );
  }

  if (!session) {
    return (
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: '#ef4444', fontSize: 14 }}>Failed to load session data.</p>
      </main>
    );
  }

  const analysis = session.analysis_results || {};
  const riskLevel = analysis.overall_risk_level || 'unknown';

  // Count pass/warning/fail
  const counts = { pass: 0, warning: 0, fail: 0 };
  for (const attr of Object.values(analysis.results || {})) {
    for (const m of Object.values((attr as any)?.metrics || {})) {
      const s = (m as any)?.status;
      if (s === 'pass') counts.pass++;
      else if (s === 'warning') counts.warning++;
      else if (s === 'fail') counts.fail++;
    }
  }

  return (
    <main style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: '#f1f5f9' }}>
            {session.model_name || 'Bias Analysis'}
          </h2>
          <p style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
            Session: {selectedSessionId}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <RegulationSelector value={regulation} onChange={setRegulation} />
          <PDFExport sessionId={selectedSessionId} />
        </div>
      </div>

      {/* Risk Card */}
      <div style={{ marginBottom: 24 }}>
        <RiskScoreCard level={riskLevel} metrics={counts} />
      </div>

      {/* Charts */}
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#f1f5f9', marginBottom: 12 }}>
          📊 Bias Dashboard
        </h3>
        <BiasCharts analysisResults={analysis} />
      </div>

      {/* Oversight Form */}
      <div style={{ maxWidth: 500, marginTop: 24 }}>
        <OversightForm sessionId={selectedSessionId} />
      </div>
    </main>
  );
}
