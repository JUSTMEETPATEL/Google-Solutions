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
import { Loader2, AlertCircle } from 'lucide-react';

export function Dashboard() {
  const { selectedSessionId, currentScanResult, regulation, setRegulation } = useAppStore();
  const [fetchedSession, setFetchedSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(false);

  // If we have a scan result in the store, use it directly.
  // Only fetch from API for sessions loaded from sidebar (persisted sessions).
  useEffect(() => {
    if (!selectedSessionId) {
      setFetchedSession(null);
      setFetchError(false);
      return;
    }
    // If the current scan result matches this session, no need to fetch
    if (currentScanResult?.session_id === selectedSessionId) {
      setFetchedSession(null);
      setFetchError(false);
      return;
    }
    // Try fetching from the API (for persisted sessions)
    setLoading(true);
    setFetchError(false);
    fetchSession(selectedSessionId)
      .then((data) => setFetchedSession(data))
      .catch(() => setFetchError(true))
      .finally(() => setLoading(false));
  }, [selectedSessionId, currentScanResult]);

  // No session selected — show upload view
  if (!selectedSessionId) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center p-8 relative z-0">
        <div className="absolute inset-0 bg-dark-900/40 backdrop-blur-3xl -z-10" />
        <FileUpload />
      </main>
    );
  }

  if (loading) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center relative z-0">
        <div className="absolute inset-0 bg-dark-900/40 backdrop-blur-3xl -z-10" />
        <Loader2 className="w-10 h-10 text-primary-500 animate-spin mb-4" />
        <p className="text-dark-400 font-medium animate-pulse">Loading analysis data...</p>
      </main>
    );
  }

  // Determine the session data source: store scan result or fetched session
  const session = currentScanResult?.session_id === selectedSessionId
    ? currentScanResult
    : fetchedSession;

  if (!session) {
    if (fetchError) {
      return (
        <main className="flex-1 flex flex-col items-center justify-center relative z-0">
          <div className="absolute inset-0 bg-dark-900/40 backdrop-blur-3xl -z-10" />
          <div className="glass-panel p-6 rounded-2xl flex flex-col items-center text-center max-w-sm">
            <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
            <p className="text-red-400 font-medium">Failed to load session data.</p>
            <p className="text-dark-400 text-sm mt-2">Please try selecting another session from the sidebar.</p>
          </div>
        </main>
      );
    }
    return (
      <main className="flex-1 flex flex-col items-center justify-center relative z-0">
        <div className="absolute inset-0 bg-dark-900/40 backdrop-blur-3xl -z-10" />
        <FileUpload />
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
    <main className="flex-1 overflow-y-auto relative z-0 p-8 lg:p-12">
      <div className="absolute inset-0 bg-dark-900/40 backdrop-blur-3xl -z-10" />
      
      <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:justify-between md:items-end gap-6 pb-6 border-b border-white/5">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-dark-300">
              {session.model_name || 'Bias Analysis Report'}
            </h2>
            <div className="flex items-center gap-3 mt-3">
              <span className="px-2.5 py-1 rounded-md bg-dark-800 text-dark-300 text-xs font-medium font-mono border border-white/5">
                ID: {selectedSessionId.substring(0, 8)}
              </span>
              {session.created_at && (
                <span className="text-sm text-dark-400">
                  {new Date(session.created_at).toLocaleString()}
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <RegulationSelector value={regulation} onChange={setRegulation} />
            <PDFExport sessionId={selectedSessionId} />
          </div>
        </header>

        {/* Risk Card */}
        <section>
          <RiskScoreCard level={riskLevel} metrics={counts} />
        </section>

        {/* Charts */}
        <section className="glass-panel p-6 rounded-3xl glow-border">
          <div className="mb-6 flex items-center gap-3">
            <div className="h-8 w-2 rounded-full bg-primary-500"></div>
            <h3 className="text-xl font-bold text-white">
              Metrics Analysis Dashboard
            </h3>
          </div>
          <BiasCharts analysisResults={analysis} />
        </section>

        {/* Oversight Form */}
        <section className="grid md:grid-cols-2 gap-8">
          <div className="glass-panel p-6 rounded-3xl">
            <div className="mb-6 flex items-center gap-3">
              <div className="h-8 w-2 rounded-full bg-purple-500"></div>
              <h3 className="text-xl font-bold text-white">
                Human Oversight
              </h3>
            </div>
            <OversightForm sessionId={selectedSessionId} />
          </div>
          
          {/* Metadata info */}
          <div className="glass-panel p-6 rounded-3xl flex flex-col justify-center">
            <div className="text-center p-6 border border-white/5 rounded-2xl bg-dark-900/50">
              <div className="inline-flex items-center justify-center p-3 rounded-full bg-primary-500/10 text-primary-400 mb-4">
                <AlertCircle className="w-8 h-8" />
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Compliance Ready</h4>
              <p className="text-sm text-dark-400 mb-6">
                Fill out the human oversight form to generate a regulation-ready audit report. This guarantees accountability per {regulation?.toUpperCase() || 'compliance'} standards.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

