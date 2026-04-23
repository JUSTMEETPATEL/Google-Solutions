/** DriftMonitor — temporal drift comparison between sessions. */

import { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, ArrowRightLeft, Loader2 } from 'lucide-react';
import { compareSessions } from '../api/client';
import { useAppStore } from '../store/appStore';
import type { DriftResult } from '../api/client';

interface DriftMonitorProps {
  currentSessionId: string;
}

const driftIcons: Record<string, any> = {
  improved: TrendingUp,
  degraded: TrendingDown,
  stable: Minus,
};

const driftColors: Record<string, { color: string; bg: string }> = {
  improved: { color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  degraded: { color: 'text-red-400', bg: 'bg-red-500/10' },
  stable: { color: 'text-zinc-400', bg: 'bg-zinc-500/10' },
};

export function DriftMonitor({ currentSessionId }: DriftMonitorProps) {
  const { sessions } = useAppStore();
  const [baselineId, setBaselineId] = useState<string>('');
  const [driftResult, setDriftResult] = useState<DriftResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const otherSessions = sessions.filter(s => s.id !== currentSessionId);

  const handleCompare = async () => {
    if (!baselineId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await compareSessions(baselineId, currentSessionId);
      setDriftResult(result);
    } catch (e: any) {
      setError(e.message || 'Drift comparison failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Session selector */}
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={baselineId}
          onChange={(e) => setBaselineId(e.target.value)}
          className="flex-1 min-w-[200px] px-3 py-2 rounded-lg bg-zinc-900 border border-white/10 text-xs font-mono text-zinc-300 focus:border-cyan-500/50 focus:outline-none transition-colors"
        >
          <option value="">Select baseline session…</option>
          {otherSessions.map(s => (
            <option key={s.id} value={s.id}>
              {s.model_name} — {s.id.substring(0, 8)} ({s.risk_level})
            </option>
          ))}
        </select>

        <button
          onClick={handleCompare}
          disabled={!baselineId || loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-xs font-bold text-white uppercase tracking-widest hover:bg-white/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <ArrowRightLeft className="w-3.5 h-3.5" />
          )}
          Compare
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 text-xs text-red-400">
          {error}
        </div>
      )}

      {/* Drift Results */}
      {driftResult && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 flex flex-col gap-4">
          {/* Summary card */}
          <div className={`${driftColors[driftResult.overall_drift]?.bg || 'bg-zinc-500/10'} rounded-xl p-4 border ${
            driftResult.overall_drift === 'degraded' ? 'border-red-500/20' :
            driftResult.overall_drift === 'improved' ? 'border-emerald-500/20' :
            'border-zinc-500/20'
          }`}>
            <div className="flex items-center gap-3 mb-2">
              {(() => {
                const Icon = driftIcons[driftResult.overall_drift] || Minus;
                const colors = driftColors[driftResult.overall_drift] || driftColors.stable;
                return <Icon className={`w-5 h-5 ${colors.color}`} />;
              })()}
              <p className={`text-sm font-bold ${driftColors[driftResult.overall_drift]?.color || 'text-zinc-400'}`}>
                {driftResult.summary}
              </p>
            </div>

            {/* Stats */}
            <div className="flex gap-4 mt-3">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-xs font-mono text-zinc-400">
                  {driftResult.stats.metrics_improved} improved
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <span className="text-xs font-mono text-zinc-400">
                  {driftResult.stats.metrics_degraded} degraded
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-zinc-500" />
                <span className="text-xs font-mono text-zinc-400">
                  {driftResult.stats.metrics_stable} stable
                </span>
              </div>
            </div>
          </div>

          {/* Alerts */}
          {driftResult.alerts.length > 0 && (
            <div className="flex flex-col gap-2">
              <p className="text-[10px] font-bold text-red-400 uppercase tracking-widest flex items-center gap-1.5">
                <AlertTriangle className="w-3 h-3" /> Threshold Crossings
              </p>
              {driftResult.alerts.map((alert, i) => (
                <div key={i} className="bg-red-500/10 border border-red-500/15 rounded-lg px-3 py-2">
                  <p className="text-xs text-red-300">{alert.message}</p>
                </div>
              ))}
            </div>
          )}

          {/* Per-attribute drift */}
          {Object.entries(driftResult.per_attribute).map(([attrName, attrData]: [string, any]) => (
            <div key={attrName}>
              <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">
                {attrName.replace(/_/g, ' ')}
              </p>
              <div className="flex flex-col gap-1">
                {Object.entries(attrData.metrics || {}).map(([metricName, metricDrift]: [string, any]) => {
                  const dir = metricDrift.direction;
                  const dirColors = driftColors[dir] || driftColors.stable;
                  return (
                    <div key={metricName} className="flex items-center justify-between py-2 px-3 rounded-lg bg-black/20">
                      <span className="text-xs font-mono text-zinc-300 truncate max-w-[150px]">
                        {metricName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                      <div className="flex items-center gap-3">
                        {metricDrift.baseline_value != null && (
                          <span className="text-[10px] font-mono text-zinc-500">
                            {metricDrift.baseline_value.toFixed(4)}
                          </span>
                        )}
                        <span className="text-zinc-600">→</span>
                        {metricDrift.current_value != null && (
                          <span className={`text-[10px] font-mono font-bold ${dirColors.color}`}>
                            {metricDrift.current_value.toFixed(4)}
                          </span>
                        )}
                        <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${dirColors.bg} ${dirColors.color} tracking-widest`}>
                          {dir}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
