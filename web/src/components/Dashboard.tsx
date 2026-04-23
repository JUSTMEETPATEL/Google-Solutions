/** Dashboard — main view assembling all analysis components. */

import { useEffect, useState } from 'react';
import { BiasCharts } from './BiasCharts';
import { RiskScoreCard } from './RiskScoreCard';
import { RegulationSelector } from './RegulationSelector';
import { OversightForm } from './OversightForm';
import { PDFExport } from './PDFExport';
import { FileUpload } from './FileUpload';
import { ExplanationsPanel } from './ExplanationsPanel';
import { IntersectionalPanel } from './IntersectionalPanel';
import { ConfidenceIntervalsPanel } from './ConfidenceIntervalsPanel';
import { FeatureAttributionPanel } from './FeatureAttributionPanel';
import { MitigationPanel } from './MitigationPanel';
import { DriftMonitor } from './DriftMonitor';
import { useAppStore } from '../store/appStore';
import { fetchSession } from '../api/client';
import {
  Loader2, AlertCircle, Fingerprint, BookOpen, Users,
  BarChart2, Layers, Zap, TrendingUp, MessageSquare
} from 'lucide-react';

type TabId = 'metrics' | 'explanations' | 'intersectional' | 'significance' | 'attribution' | 'mitigation' | 'drift';

const TABS: { id: TabId; label: string; icon: any }[] = [
  { id: 'metrics', label: 'Metrics', icon: BarChart2 },
  { id: 'explanations', label: 'Explanations', icon: MessageSquare },
  { id: 'intersectional', label: 'Intersectional', icon: Users },
  { id: 'significance', label: 'Significance', icon: BarChart2 },
  { id: 'attribution', label: 'Attribution', icon: Layers },
  { id: 'mitigation', label: 'Mitigation', icon: Zap },
  { id: 'drift', label: 'Drift', icon: TrendingUp },
];

export function Dashboard() {
  const { selectedSessionId, currentScanResult, regulation, setRegulation } = useAppStore();
  const [fetchedSession, setFetchedSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>('metrics');

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
  const explanations = session.explanations || {};
  const intersectional = session.intersectional_analysis;
  const confidenceIntervals = session.confidence_intervals;
  const featureAttribution = session.feature_attribution;
  const recommendations = session.recommendations || [];
  const mitigationHistory = session.mitigation_history || [];

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

        {/* Top Stats Row */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Risk & Oversight (3 cols) */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            <section>
              <RiskScoreCard level={riskLevel} metrics={counts} />
            </section>

            <section className="glass-panel p-6 rounded-2xl flex-1">
              <div className="mb-4 flex items-center gap-2">
                <div className="h-4 w-1 rounded-sm bg-purple-500"></div>
                <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                  Human Oversight
                </h3>
              </div>
              <OversightForm sessionId={selectedSessionId} />
            </section>
          </div>

          {/* Middle + Right: Tab Navigation + Content (9 cols) */}
          <div className="lg:col-span-9 flex flex-col gap-4">
            
            {/* Tab Navigation */}
            <nav className="flex gap-1 p-1 bg-dark-950/60 rounded-xl border border-white/5 overflow-x-auto">
              {TABS.map(tab => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                // Show badge for intersectional/attribution if data exists
                let hasBadge = false;
                if (tab.id === 'intersectional' && intersectional?.intersections?.length) hasBadge = true;
                if (tab.id === 'attribution' && featureAttribution?.bias_drivers?.length) hasBadge = true;
                if (tab.id === 'mitigation' && recommendations.length > 0 && recommendations[0]?.algorithm !== 'none') hasBadge = true;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-all duration-200 whitespace-nowrap ${
                      isActive
                        ? 'bg-white/10 text-white shadow-sm'
                        : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {tab.label}
                    {hasBadge && (
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                    )}
                  </button>
                );
              })}
            </nav>

            {/* Tab Content */}
            <section className="glass-panel p-6 rounded-2xl glow-border min-h-[400px]">
              <div className="mb-5 flex items-center gap-2">
                <div className="h-4 w-1 rounded-sm bg-primary-500"></div>
                <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                  {TABS.find(t => t.id === activeTab)?.label || 'Analysis'}
                </h3>
              </div>

              {activeTab === 'metrics' && (
                <div className="pr-2">
                  <BiasCharts analysisResults={analysis} />
                </div>
              )}

              {activeTab === 'explanations' && (
                <ExplanationsPanel explanations={explanations} />
              )}

              {activeTab === 'intersectional' && (
                intersectional ? (
                  <IntersectionalPanel data={intersectional} />
                ) : (
                  <EmptyState
                    icon={Users}
                    title="No Intersectional Data"
                    description="Intersectional analysis requires 2+ protected attributes in the dataset."
                  />
                )
              )}

              {activeTab === 'significance' && (
                confidenceIntervals ? (
                  <ConfidenceIntervalsPanel data={confidenceIntervals} />
                ) : (
                  <EmptyState
                    icon={BarChart2}
                    title="Significance Testing Unavailable"
                    description="Bootstrap confidence intervals could not be computed for this scan."
                  />
                )
              )}

              {activeTab === 'attribution' && (
                featureAttribution ? (
                  <FeatureAttributionPanel data={featureAttribution} />
                ) : (
                  <EmptyState
                    icon={Layers}
                    title="Feature Attribution Unavailable"
                    description="Permutation importance could not be computed for this model."
                  />
                )
              )}

              {activeTab === 'mitigation' && (
                <MitigationPanel
                  sessionId={selectedSessionId}
                  recommendations={recommendations}
                  mitigationHistory={mitigationHistory}
                />
              )}

              {activeTab === 'drift' && (
                <DriftMonitor currentSessionId={selectedSessionId} />
              )}
            </section>
          </div>
        </div>

        {/* Compliance Status Footer */}
        <section className="glass-panel p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute -right-12 -bottom-12 opacity-5 pointer-events-none">
            <Fingerprint className="w-64 h-64 text-primary-500" />
          </div>
          <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h4 className="text-sm font-bold text-white mb-1 uppercase tracking-widest">
                Compliance Status
              </h4>
              <p className="text-sm text-dark-300 leading-relaxed text-balance">
                Audit generated under <span className="text-white font-semibold">{regulation?.toUpperCase() || 'STANDARD'}</span>.
                {recommendations.length > 0 && recommendations[0]?.algorithm !== 'none'
                  ? ` ${recommendations.length} mitigation strategies recommended.`
                  : ' All metrics within acceptable thresholds.'
                }
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-dark-500 font-bold mb-1">Session</p>
                <p className="text-xs font-mono text-dark-400">{selectedSessionId.substring(0, 16)}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-widest text-dark-500 font-bold mb-1">Risk</p>
                <p className={`text-xs font-bold uppercase tracking-widest ${
                  riskLevel === 'high' ? 'text-red-400' :
                  riskLevel === 'medium' ? 'text-amber-400' :
                  'text-emerald-400'
                }`}>
                  {riskLevel}
                </p>
              </div>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}

/** Empty state placeholder for tabs without data. */
function EmptyState({ icon: Icon, title, description }: { icon: any; title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="p-4 bg-dark-800 rounded-full mb-4 border border-white/5">
        <Icon className="w-8 h-8 text-zinc-500" />
      </div>
      <p className="text-sm font-bold text-zinc-400 uppercase tracking-widest mb-2">{title}</p>
      <p className="text-xs text-zinc-500 max-w-sm">{description}</p>
    </div>
  );
}
