/** ExplanationsPanel — plain-English metric explanations for compliance officers. */

import { AlertCircle, CheckCircle2, AlertTriangle, BookOpen } from 'lucide-react';
import type { MetricExplanation } from '../api/client';

interface ExplanationsPanelProps {
  explanations: Record<string, Record<string, MetricExplanation>>;
}

const severityConfig: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  pass: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  fail: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  skipped: { icon: BookOpen, color: 'text-zinc-400', bg: 'bg-zinc-500/10', border: 'border-zinc-500/20' },
};

export function ExplanationsPanel({ explanations }: ExplanationsPanelProps) {
  if (!explanations || Object.keys(explanations).length === 0) return null;

  return (
    <div className="flex flex-col gap-6">
      {Object.entries(explanations).map(([attrName, metrics]) => (
        <div key={attrName} className="animate-in fade-in duration-500">
          <div className="flex items-center gap-3 mb-4 pl-2 border-l-2 border-cyan-500">
            <h3 className="text-sm font-black text-white uppercase tracking-widest">
              {attrName.replace(/_/g, ' ')}
            </h3>
          </div>
          <div className="flex flex-col gap-3">
            {Object.entries(metrics).map(([metricName, explanation]) => {
              const config = severityConfig[explanation.severity] || severityConfig.skipped;
              const Icon = config.icon;
              return (
                <div
                  key={metricName}
                  className={`${config.bg} border ${config.border} rounded-xl p-4 transition-all duration-300 hover:scale-[1.01]`}
                >
                  <div className="flex items-start gap-3">
                    <Icon className={`w-5 h-5 ${config.color} mt-0.5 flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${config.color} mb-1`}>
                        {explanation.summary}
                      </p>
                      <p className="text-xs text-zinc-400 leading-relaxed mb-2">
                        {explanation.detail}
                      </p>
                      <div className="flex items-center gap-2 px-2.5 py-1.5 bg-black/20 rounded-lg w-fit">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Recommendation</span>
                        <span className="text-xs text-zinc-300">{explanation.recommendation}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
