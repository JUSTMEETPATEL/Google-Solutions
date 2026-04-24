/** MitigationPanel — auto-recommendations and live mitigation execution with before/after. */

import { useState } from 'react';
import { Zap, Shield, CheckCircle2, Loader2, ArrowUp, ArrowDown, Minus, TrendingUp } from 'lucide-react';
import { applyMitigation } from '../api/client';
import { showToast } from './Toast';
import type { MitigationRecommendation } from '../api/client';

interface MitigationPanelProps {
  sessionId: string;
  recommendations: MitigationRecommendation[];
  mitigationHistory?: any[];
}

const confidenceColors: Record<string, { color: string; bg: string }> = {
  high: { color: 'text-emerald-400', bg: 'bg-emerald-500/15' },
  medium: { color: 'text-amber-400', bg: 'bg-amber-500/15' },
  low: { color: 'text-red-400', bg: 'bg-red-500/15' },
};

const categoryIcons: Record<string, string> = {
  'pre-processing': '🔄',
  'in-processing': '⚡',
  'post-processing': '🎯',
  'none': '✅',
};

export function MitigationPanel({ sessionId, recommendations, mitigationHistory }: MitigationPanelProps) {
  const [applying, setApplying] = useState<string | null>(null);
  const [appliedResults, setAppliedResults] = useState<Record<string, any>>({});
  const [appliedAlgorithms, setAppliedAlgorithms] = useState<Set<string>>(
    new Set((mitigationHistory || []).map((m: any) => m.algorithm))
  );
  const [error, setError] = useState<string | null>(null);

  // Pre-populate results from history
  const getResultForAlgo = (algo: string) => {
    if (appliedResults[algo]) return appliedResults[algo];
    const hist = (mitigationHistory || []).find((m: any) => m.algorithm === algo);
    if (hist?.improvement_summary) return hist;
    return null;
  };

  const handleApply = async (algorithm: string) => {
    setApplying(algorithm);
    setError(null);
    try {
      const response = await applyMitigation(sessionId, algorithm);
      setAppliedAlgorithms(prev => new Set([...prev, algorithm]));

      if (response.mitigation_result) {
        setAppliedResults(prev => ({ ...prev, [algorithm]: response.mitigation_result }));
      }

      if (response.status === 'executed') {
        showToast(`Mitigation "${algorithm.replace(/_/g, ' ')}" executed successfully`, 'success');
      } else {
        showToast(`Mitigation "${algorithm.replace(/_/g, ' ')}" recorded`, 'info');
      }
    } catch (e: any) {
      setError(e.message || 'Mitigation failed');
      showToast('Mitigation failed: ' + (e.message || 'Unknown error'), 'error');
    } finally {
      setApplying(null);
    }
  };

  if (!recommendations || recommendations.length === 0) return null;

  if (recommendations.length === 1 && recommendations[0].algorithm === 'none') {
    return (
      <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-5 flex items-center gap-3 animate-in fade-in duration-500">
        <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
        <div>
          <p className="text-sm font-bold text-emerald-400">No Mitigation Needed</p>
          <p className="text-xs text-zinc-400 mt-1">{recommendations[0].rationale}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-amber-400" />
        <p className="text-[10px] font-bold text-amber-400 uppercase tracking-widest">
          {recommendations.length} Mitigation Strategies — Ranked by Confidence
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 text-xs text-red-400">{error}</div>
      )}

      <div className="flex flex-col gap-3">
        {recommendations.map((rec) => {
          const conf = confidenceColors[rec.confidence] || confidenceColors.medium;
          const isApplied = appliedAlgorithms.has(rec.algorithm);
          const isApplying = applying === rec.algorithm;
          const result = getResultForAlgo(rec.algorithm);

          return (
            <div
              key={rec.algorithm}
              className={`rounded-xl border transition-all duration-300 ${
                isApplied ? 'bg-emerald-500/5 border-emerald-500/20' : 'glass-panel border-white/5 hover:border-white/10'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span className="text-lg leading-none">{categoryIcons[rec.category] || '📊'}</span>
                      <span className="text-sm font-bold text-white">
                        {rec.algorithm.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                      <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${conf.bg} ${conf.color} tracking-widest`}>
                        {rec.confidence}
                      </span>
                      <span className="text-[9px] font-mono text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded">
                        {rec.category}
                      </span>
                      {isApplied && (
                        <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 tracking-widest flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Executed
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-zinc-400 leading-relaxed mb-2">{rec.rationale}</p>
                    <div className="flex gap-1.5 flex-wrap">
                      {rec.addresses.map(metric => (
                        <span key={metric} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          {metric.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>

                  {!isApplied && (
                    <button
                      onClick={() => handleApply(rec.algorithm)}
                      disabled={isApplying}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-bold text-white uppercase tracking-widest hover:bg-white/10 hover:border-white/20 transition-all duration-200 flex-shrink-0 disabled:opacity-50"
                    >
                      {isApplying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Shield className="w-3.5 h-3.5" />}
                      Execute
                    </button>
                  )}
                </div>

                {/* Before/After Results */}
                {result?.improvement_summary && (
                  <div className="mt-4 pt-3 border-t border-white/5 animate-in fade-in duration-500">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-3.5 h-3.5 text-primary-500" />
                      <span className="text-[10px] font-bold text-primary-400 uppercase tracking-widest">Before / After Results</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 mb-3">
                      <MiniStat label="Improved" value={result.improvement_summary.improved} color="text-emerald-400" />
                      <MiniStat label="Degraded" value={result.improvement_summary.degraded} color="text-red-400" />
                      <MiniStat label="Unchanged" value={result.improvement_summary.unchanged} color="text-zinc-400" />
                    </div>
                    {result.improvement_summary.details && (
                      <div className="space-y-1">
                        {result.improvement_summary.details.slice(0, 6).map((d: any, i: number) => (
                          <div key={i} className="flex items-center justify-between text-[11px] px-2 py-1 rounded bg-dark-900/50">
                            <span className="text-zinc-300">{d.metric?.replace(/_/g, ' ')}</span>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-zinc-500">{d.before_value?.toFixed(3) ?? '—'}</span>
                              <span className="text-zinc-600">→</span>
                              <span className="font-mono text-zinc-300">{d.after_value?.toFixed(3) ?? '—'}</span>
                              <ChangeIcon change={d.change} />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function MiniStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-lg bg-dark-900/60 p-2 text-center">
      <div className={`text-base font-bold ${color}`}>{value}</div>
      <div className="text-[8px] font-bold text-zinc-600 uppercase tracking-widest">{label}</div>
    </div>
  );
}

function ChangeIcon({ change }: { change: string }) {
  if (change === 'improved') return <ArrowUp className="w-3 h-3 text-emerald-400" />;
  if (change === 'degraded') return <ArrowDown className="w-3 h-3 text-red-400" />;
  return <Minus className="w-3 h-3 text-zinc-600" />;
}
