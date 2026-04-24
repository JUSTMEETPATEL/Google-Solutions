/** ComparisonPanel — side-by-side model/session comparison view. */

import { useState } from 'react';
import { GitCompareArrows, ArrowUp, ArrowDown, Minus, Loader2, AlertCircle } from 'lucide-react';
import { compareSessions as apiCompareSessions } from '../api/client';
import { useAppStore } from '../store/appStore';

interface ComparisonPanelProps {
  currentSessionId: string;
}

export function ComparisonPanel({ currentSessionId }: ComparisonPanelProps) {
  const { sessions } = useAppStore();
  const [compareId, setCompareId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const otherSessions = sessions.filter(s => s.id !== currentSessionId);

  const handleCompare = async () => {
    if (!compareId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiCompareSessions(compareId, currentSessionId);
      setResult(res);
    } catch (e: any) {
      setError(e.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Session Picker */}
      <div className="flex items-end gap-3 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1.5">
            Compare Against (Baseline)
          </label>
          <select
            value={compareId}
            onChange={e => { setCompareId(e.target.value); setResult(null); }}
            className="w-full px-3 py-2.5 rounded-lg bg-dark-900 border border-white/10 text-sm text-white focus:outline-none focus:border-primary-500 transition-colors"
          >
            <option value="">Select a session…</option>
            {otherSessions.map(s => (
              <option key={s.id} value={s.id}>
                {s.model_name || 'Unknown'} — {s.created_at?.slice(0, 10)} ({s.risk_level})
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleCompare}
          disabled={!compareId || loading}
          className="px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-xs font-bold uppercase tracking-widest text-white hover:bg-white/10 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitCompareArrows className="w-4 h-4" />}
          Compare
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 flex items-center gap-2 text-xs text-red-400">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="animate-in fade-in duration-500 flex flex-col gap-5">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <SummaryCard label="Risk Change" value={result.summary.risk_change} />
            <SummaryCard label="Improved" value={result.summary.improved} color="text-emerald-400" />
            <SummaryCard label="Degraded" value={result.summary.degraded} color="text-red-400" />
            <SummaryCard label="Unchanged" value={result.summary.unchanged} color="text-zinc-400" />
          </div>

          {/* Session Headers */}
          <div className="grid grid-cols-2 gap-3">
            <SessionHeader label="Baseline (A)" data={result.session_a} />
            <SessionHeader label="Current (B)" data={result.session_b} />
          </div>

          {/* Metric Comparison Table */}
          {Object.entries(result.comparison as Record<string, Record<string, any>>).map(([attr, metrics]) => (
            <div key={attr}>
              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-2">
                {attr.replace(/_/g, ' ')}
              </h4>
              <div className="overflow-x-auto rounded-lg border border-white/5">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-dark-900/80">
                      <th className="text-left px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Metric</th>
                      <th className="text-center px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Baseline</th>
                      <th className="text-center px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Current</th>
                      <th className="text-center px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Delta</th>
                      <th className="text-center px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(metrics).map(([mName, mData]: [string, any]) => (
                      <tr key={mName} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                        <td className="px-3 py-2 text-white font-medium">{mName.replace(/_/g, ' ')}</td>
                        <td className="px-3 py-2 text-center">
                          <StatusBadge value={mData.session_a.value} status={mData.session_a.status} />
                        </td>
                        <td className="px-3 py-2 text-center">
                          <StatusBadge value={mData.session_b.value} status={mData.session_b.status} />
                        </td>
                        <td className="px-3 py-2 text-center font-mono text-xs text-zinc-400">
                          {mData.delta != null ? (mData.delta >= 0 ? '+' : '') + mData.delta.toFixed(4) : '—'}
                        </td>
                        <td className="px-3 py-2 text-center">
                          <ChangeIndicator change={mData.change} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}

      {!result && !loading && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="p-4 bg-dark-800 rounded-full mb-4 border border-white/5">
            <GitCompareArrows className="w-8 h-8 text-zinc-500" />
          </div>
          <p className="text-sm font-bold text-zinc-400 uppercase tracking-widest mb-2">Model Comparison</p>
          <p className="text-xs text-zinc-500 max-w-sm">
            Select a baseline session above to compare metrics side-by-side. Use this to track pre- vs post-mitigation changes or compare candidate models.
          </p>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: any; color?: string }) {
  return (
    <div className="glass-panel rounded-xl p-3 text-center">
      <div className={`text-lg font-bold ${color || 'text-white'}`}>{String(value)}</div>
      <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mt-1">{label}</div>
    </div>
  );
}

function SessionHeader({ label, data }: { label: string; data: any }) {
  const riskColor = data.risk_level === 'high' ? 'text-red-400' : data.risk_level === 'medium' ? 'text-amber-400' : 'text-emerald-400';
  return (
    <div className="glass-panel rounded-xl p-3">
      <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-1">{label}</div>
      <div className="text-sm font-bold text-white truncate">{data.model_name || 'Unknown'}</div>
      <div className="flex items-center justify-between mt-1">
        <span className="text-[10px] font-mono text-zinc-500">{data.id?.substring(0, 10)}</span>
        <span className={`text-[10px] font-bold uppercase tracking-widest ${riskColor}`}>{data.risk_level}</span>
      </div>
    </div>
  );
}

function StatusBadge({ value, status }: { value: number | null; status: string }) {
  const color = status === 'pass' ? 'text-emerald-400' : status === 'fail' ? 'text-red-400' : status === 'warning' ? 'text-amber-400' : 'text-zinc-500';
  return (
    <span className={`font-mono text-xs ${color}`}>
      {value != null ? value.toFixed(4) : '—'}
    </span>
  );
}

function ChangeIndicator({ change }: { change: string }) {
  if (change === 'improved') return <span className="inline-flex items-center gap-1 text-emerald-400 text-[10px] font-bold uppercase tracking-widest"><ArrowUp className="w-3 h-3" />Better</span>;
  if (change === 'degraded') return <span className="inline-flex items-center gap-1 text-red-400 text-[10px] font-bold uppercase tracking-widest"><ArrowDown className="w-3 h-3" />Worse</span>;
  return <span className="inline-flex items-center gap-1 text-zinc-500 text-[10px] font-bold uppercase tracking-widest"><Minus className="w-3 h-3" />Same</span>;
}
