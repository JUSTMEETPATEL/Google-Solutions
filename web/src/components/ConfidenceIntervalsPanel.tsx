/** ConfidenceIntervalsPanel — shows bootstrap confidence intervals for statistical significance. */

import { BarChart2, Info } from 'lucide-react';
import type { ConfidenceInterval } from '../api/client';

interface ConfidenceIntervalsPanelProps {
  data: Record<string, Record<string, ConfidenceInterval>>;
}

export function ConfidenceIntervalsPanel({ data }: ConfidenceIntervalsPanelProps) {
  if (!data || Object.keys(data).length === 0) return null;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2 px-3 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg w-fit">
        <Info className="w-3.5 h-3.5 text-cyan-400" />
        <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">
          95% Bootstrap Confidence Intervals — statistically significant bias is highlighted
        </span>
      </div>

      {Object.entries(data).map(([attrName, metrics]) => (
        <div key={attrName} className="animate-in fade-in duration-500">
          <div className="flex items-center gap-3 mb-4 pl-2 border-l-2 border-teal-500">
            <BarChart2 className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-black text-white uppercase tracking-widest">
              {attrName.replace(/_/g, ' ')}
            </h3>
          </div>

          <div className="grid gap-2">
            {Object.entries(metrics).map(([metricName, ci]) => (
              <CIRow key={metricName} metricName={metricName} ci={ci} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function CIRow({ metricName, ci }: { metricName: string; ci: ConfidenceInterval }) {
  if (ci.point_estimate == null) {
    return (
      <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-black/20 opacity-50">
        <span className="text-xs font-mono text-zinc-400">
          {metricName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
        </span>
        <span className="text-xs text-zinc-500">{ci.note || 'Unavailable'}</span>
      </div>
    );
  }

  const hasCI = ci.ci_lower != null && ci.ci_upper != null;
  const ciWidth = hasCI ? Math.abs(ci.ci_upper! - ci.ci_lower!) : 0;

  return (
    <div className={`flex items-center gap-4 py-3 px-4 rounded-xl transition-all duration-300 ${
      ci.is_significant
        ? 'bg-red-500/10 border border-red-500/20'
        : 'bg-black/20 border border-transparent'
    }`}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-mono text-zinc-300 truncate">
            {metricName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </span>
          {ci.is_significant && (
            <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 tracking-widest">
              Significant
            </span>
          )}
        </div>

        {/* Visual CI bar */}
        {hasCI && (
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-[10px] font-mono text-zinc-500 w-12 text-right">
              {ci.ci_lower!.toFixed(3)}
            </span>
            <div className="flex-1 h-3 bg-zinc-800 rounded-full relative overflow-hidden">
              {/* CI range bar */}
              <div
                className={`absolute h-full rounded-full ${ci.is_significant ? 'bg-red-500/60' : 'bg-cyan-500/40'}`}
                style={{
                  left: `${Math.max(0, Math.min(100, ci.ci_lower! * 100))}%`,
                  width: `${Math.max(2, Math.min(100, ciWidth * 100))}%`,
                }}
              />
              {/* Point estimate marker */}
              <div
                className={`absolute top-0 bottom-0 w-0.5 ${ci.is_significant ? 'bg-red-400' : 'bg-cyan-400'}`}
                style={{ left: `${Math.max(0, Math.min(100, ci.point_estimate * 100))}%` }}
              />
            </div>
            <span className="text-[10px] font-mono text-zinc-500 w-12">
              {ci.ci_upper!.toFixed(3)}
            </span>
          </div>
        )}
      </div>

      <div className="text-right flex-shrink-0">
        <div className={`text-sm font-mono font-bold ${ci.is_significant ? 'text-red-400' : 'text-cyan-400'}`}>
          {ci.point_estimate.toFixed(4)}
        </div>
        <div className="text-[9px] text-zinc-500 font-mono">
          n={ci.n_bootstrap}
        </div>
      </div>
    </div>
  );
}
