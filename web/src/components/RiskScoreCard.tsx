/** RiskScoreCard — overall risk level display (WEB-05). */
import { AlertOctagon, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';

const RISK_CONFIG: Record<string, { color: string; bg: string; icon: any, textClass: string }> = {
  high: { color: 'text-red-500', bg: 'bg-red-500/10 border-red-500/20', icon: AlertOctagon, textClass: 'text-red-500' },
  medium: { color: 'text-yellow-500', bg: 'bg-yellow-500/10 border-yellow-500/20', icon: AlertTriangle, textClass: 'text-yellow-500' },
  low: { color: 'text-emerald-500', bg: 'bg-emerald-500/10 border-emerald-500/20', icon: CheckCircle2, textClass: 'text-emerald-500' },
  unknown: { color: 'text-dark-400', bg: 'bg-dark-800 border-white/5', icon: HelpCircle, textClass: 'text-dark-400' },
};

interface RiskScoreCardProps {
  level: string;
  metrics?: { pass: number; warning: number; fail: number };
}

export function RiskScoreCard({ level, metrics }: RiskScoreCardProps) {
  const config = RISK_CONFIG[level.toLowerCase()] || RISK_CONFIG.unknown;
  const Icon = config.icon;

  return (
    <div className={`rounded-3xl border p-8 flex items-center gap-6 backdrop-blur-md shadow-xl transition-all duration-500 hover:shadow-2xl ${config.bg} relative overflow-hidden group`}>
      {/* Decorative gradient orb */}
      <div className={`absolute -right-20 -top-20 w-40 h-40 blur-[80px] rounded-full opacity-20 transition-opacity group-hover:opacity-40 ${config.bg.split(' ')[0]}`} />
      
      <div className={`p-4 rounded-2xl ${config.bg.split(' ')[0]} bg-opacity-20 flex-shrink-0`}>
        <Icon className={`w-12 h-12 ${config.color}`} />
      </div>
      <div className="flex-1 relative z-10">
        <div className="text-xs font-bold text-dark-400 uppercase tracking-widest mb-1">
          Overall Risk Assessment
        </div>
        <div className={`text-4xl font-extrabold tracking-tight ${config.textClass} drop-shadow-sm`}>
          {level.toUpperCase()}
        </div>
        {metrics && (
          <div className="flex items-center gap-6 mt-4">
            <div className="flex items-center gap-2 bg-dark-900/40 px-3 py-1.5 rounded-lg border border-white/5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span className="text-sm font-semibold text-emerald-100">{metrics.pass} <span className="text-emerald-500/70 font-normal">Passed</span></span>
            </div>
            <div className="flex items-center gap-2 bg-dark-900/40 px-3 py-1.5 rounded-lg border border-white/5">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-semibold text-yellow-100">{metrics.warning} <span className="text-yellow-500/70 font-normal">Warnings</span></span>
            </div>
            <div className="flex items-center gap-2 bg-dark-900/40 px-3 py-1.5 rounded-lg border border-white/5">
              <AlertOctagon className="w-4 h-4 text-red-500" />
              <span className="text-sm font-semibold text-red-100">{metrics.fail} <span className="text-red-500/70 font-normal">Failed</span></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
