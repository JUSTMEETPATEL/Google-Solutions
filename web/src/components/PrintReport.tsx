import { BiasCharts } from './BiasCharts';
import { RiskScoreCard } from './RiskScoreCard';
import { ExplanationsPanel } from './ExplanationsPanel';
import { IntersectionalPanel } from './IntersectionalPanel';
import { ConfidenceIntervalsPanel } from './ConfidenceIntervalsPanel';
import { FeatureAttributionPanel } from './FeatureAttributionPanel';
import { MitigationPanel } from './MitigationPanel';
import { Fingerprint } from 'lucide-react';

export function PrintReport({ session, regulation, oversightReviewer, oversightDecision, oversightDate }: any) {
  if (!session) return null;

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
    <div 
      id="print-report" 
      className="w-[1200px] bg-dark-950 text-white p-12 flex flex-col gap-10"
    >
      {/* Header */}
      <header className="border-b border-white/10 pb-8">
        <h1 className="text-4xl font-black mb-2 uppercase tracking-tight">FairCheck Audit Report</h1>
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-xl font-bold text-zinc-300">{session.model_name || 'Unknown Model'}</h2>
            <div className="flex gap-4 mt-4">
              <span className="flex items-center gap-1.5 px-3 py-1 bg-dark-900 rounded border border-white/10 font-mono text-sm">
                <Fingerprint className="w-4 h-4" /> {session.session_id}
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1 bg-dark-900 rounded border border-white/10 font-mono text-sm">
                {new Date(session.created_at || Date.now()).toLocaleString()}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-1">Regulation</p>
            <p className="text-lg font-bold text-primary-400">{regulation?.toUpperCase() || 'STANDARD'}</p>
          </div>
        </div>
      </header>

      {/* 1. Executive Summary */}
      <section>
        <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">1. Executive Summary</h3>
        <div className="w-full">
          <RiskScoreCard level={riskLevel} metrics={counts} />
        </div>
      </section>

      {/* 2. Fairness Metrics */}
      <section>
        <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">2. Fairness Metrics</h3>
        <div className="glass-panel p-8 rounded-2xl">
          <BiasCharts analysisResults={analysis} />
        </div>
      </section>

      {/* 3. Explanations */}
      {Object.keys(explanations).length > 0 && (
        <section>
          <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">3. Metric Explanations</h3>
          <div className="glass-panel p-8 rounded-2xl">
            <ExplanationsPanel explanations={explanations} />
          </div>
        </section>
      )}

      {/* 4. Intersectional Analysis */}
      {intersectional && intersectional.intersections?.length > 0 && (
        <section>
          <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">4. Intersectional Analysis</h3>
          <div className="glass-panel p-8 rounded-2xl">
            <IntersectionalPanel data={intersectional} />
          </div>
        </section>
      )}

      {/* 5. Significance Testing */}
      {confidenceIntervals && Object.keys(confidenceIntervals).length > 0 && (
        <section>
          <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">5. Significance Testing</h3>
          <div className="glass-panel p-8 rounded-2xl">
            <ConfidenceIntervalsPanel data={confidenceIntervals} />
          </div>
        </section>
      )}

      {/* 6. Feature Attribution */}
      {featureAttribution && featureAttribution.global_importance && (
        <section>
          <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">6. Feature Attribution & Bias Drivers</h3>
          <div className="glass-panel p-8 rounded-2xl">
            <FeatureAttributionPanel data={featureAttribution} />
          </div>
        </section>
      )}

      {/* 7. Mitigation Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <section>
          <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">7. Mitigation Strategies</h3>
          <div className="glass-panel p-8 rounded-2xl">
            <MitigationPanel sessionId={session.session_id} recommendations={recommendations} mitigationHistory={mitigationHistory} />
          </div>
        </section>
      )}

      {/* 8. Human Oversight */}
      <section className="mb-20">
        <h3 className="text-2xl font-black uppercase tracking-widest mb-6 border-l-4 border-primary-500 pl-4">8. Human Oversight & Sign-off</h3>
        <div className="glass-panel p-8 rounded-2xl flex flex-col gap-6">
          <div className="grid grid-cols-3 gap-8">
            <div>
              <p className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-2">Reviewer</p>
              <p className="text-lg font-semibold">{oversightReviewer || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-2">Decision</p>
              <p className={`text-lg font-black uppercase tracking-widest ${oversightDecision === 'approved' ? 'text-emerald-400' : 'text-red-400'}`}>
                {oversightDecision || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-2">Date</p>
              <p className="text-lg font-semibold">{oversightDate || 'N/A'}</p>
            </div>
          </div>
          <div className="mt-10 border-t border-white/10 pt-8 flex justify-between items-end">
            <div>
              <div className="w-64 border-b border-white/30 pb-2 mb-2"></div>
              <p className="text-sm text-zinc-500 font-medium">Authorized Signature</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-zinc-600 font-mono">Generated by FairCheck Platform</p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
