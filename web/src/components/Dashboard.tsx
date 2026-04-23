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
import { Loader2, AlertCircle, Fingerprint } from 'lucide-react';

export function Dashboard() {
  const { selectedSessionId, currentScanResult, regulation, setRegulation } = useAppStore();
  const [fetchedSession, setFetchedSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(false);

  useEffect(() => {
    if (!selectedSessionId) {
      setFetchedSession(null);
      setFetchError(false);
      return;
    }
    if (currentScanResult?.session_id === selectedSessionId) {
      setFetchedSession(null);
      setFetchError(false);
      return;
    }
    setLoading(true);
    setFetchError(false);
    fetchSession(selectedSessionId)
      .then((data) => setFetchedSession(data))
      .catch(() => setFetchError(true))
      .finally(() => setLoading(false));
  }, [selectedSessionId, currentScanResult]);

  if (!selectedSessionId) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center p-6 relative z-0">
        <FileUpload />
      </main>
    );
  }

  if (loading) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center relative z-0">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin mb-4" />
        <p className="text-dark-400 text-sm font-medium animate-pulse tracking-widest uppercase">Loading Audit Data...</p>
      </main>
    );
  }

  const session = currentScanResult?.session_id === selectedSessionId ? currentScanResult : fetchedSession;

  if (!session) {
    if (fetchError) {
      return (
        <main className="flex-1 flex flex-col items-center justify-center relative z-0">
          <div className="glass-panel p-6 rounded-2xl flex flex-col items-center text-center max-w-sm">
            <AlertCircle className="w-10 h-10 text-danger-500 mb-3" />
            <p className="text-danger-500 text-sm font-bold uppercase tracking-wider">Failed to load session</p>
          </div>
        </main>
      );
    }
    return (
      <main className="flex-1 flex flex-col items-center justify-center p-6 relative z-0">
        <FileUpload />
      </main>
    );
  }

  const analysis = session.analysis_results || {};
  const riskLevel = analysis.overall_risk_level || 'unknown';

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
    <main className="flex-1 overflow-y-auto relative z-0 p-6">
      <div className="max-w-[1400px] mx-auto animate-in fade-in zoom-in-95 duration-500 flex flex-col gap-6">
        
        {/* Header Bar */}
        <header className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 pb-4 border-b border-white/5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              {session.model_name || 'Audit Report'}
            </h2>
            <div className="flex items-center gap-3 mt-2">
              <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-dark-900 text-dark-300 text-[10px] font-bold font-mono border border-white/5 tracking-widest uppercase">
                <Fingerprint className="w-3 h-3" />
                {selectedSessionId.substring(0, 12)}
              </span>
              {session.created_at && (
                <span className="text-xs text-dark-400 font-medium">
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

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Top Left: Risk Score */}
          <section className="lg:col-span-4">
            <RiskScoreCard level={riskLevel} metrics={counts} />
          </section>

          {/* Top Right & Middle: Charts */}
          <section className="lg:col-span-8 glass-panel p-5 rounded-2xl glow-border">
            <div className="mb-4 flex items-center gap-2">
              <div className="h-4 w-1 rounded-sm bg-primary-500"></div>
              <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                Metrics Analysis
              </h3>
            </div>
            <div className="max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              <BiasCharts analysisResults={analysis} />
            </div>
          </section>

          {/* Bottom Left: Oversight Form */}
          <section className="lg:col-span-5 glass-panel p-5 rounded-2xl">
            <div className="mb-4 flex items-center gap-2">
              <div className="h-4 w-1 rounded-sm bg-purple-500"></div>
              <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                Human Oversight
              </h3>
            </div>
            <OversightForm sessionId={selectedSessionId} />
          </section>
          
          {/* Bottom Right: Metadata/Info */}
          <section className="lg:col-span-7 glass-panel p-5 rounded-2xl flex flex-col justify-center relative overflow-hidden">
             {/* Subtle graphic background */}
             <div className="absolute -right-20 -bottom-20 opacity-5 pointer-events-none">
               <Fingerprint className="w-96 h-96" />
             </div>
             <div className="relative z-10 max-w-md">
                <div className="inline-flex items-center justify-center p-2 rounded-lg bg-dark-800 border border-white/5 text-primary-500 mb-3">
                  <AlertCircle className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white mb-2 uppercase tracking-widest">Compliance Status</h4>
                <p className="text-sm text-dark-300 leading-relaxed text-balance">
                  This audit is generated under the <span className="text-white font-semibold">{regulation?.toUpperCase() || 'STANDARD'}</span> framework. 
                  Complete the human oversight log to finalize the audit and enable the generation of a legally compliant PDF report for external review.
                </p>
             </div>
          </section>

        </div>
      </div>
    </main>
  );
}

