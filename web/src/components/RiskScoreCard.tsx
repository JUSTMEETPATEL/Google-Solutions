/** RiskScoreCard — overall risk level display (WEB-05). */
import { AlertOctagon, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';

const RISK_CONFIG: Record<string, { color: string; bg: string; icon: any, textClass: string }> = {
  high: { color: 'text-danger-500', bg: 'bg-danger-500/10 border-danger-500/20', icon: AlertOctagon, textClass: 'text-danger-500' },
  medium: { color: 'text-warning-500', bg: 'bg-warning-500/10 border-warning-500/20', icon: AlertTriangle, textClass: 'text-warning-500' },
  low: { color: 'text-success-500', bg: 'bg-success-500/10 border-success-500/20', icon: CheckCircle2, textClass: 'text-success-500' },
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
    <div className={`h-full rounded-2xl border p-5 flex flex-col justify-between backdrop-blur-md shadow-lg ${config.bg} relative overflow-hidden group`}>
      {/* Decorative gradient orb */}
      <div className={`absolute -right-10 -top-10 w-32 h-32 blur-[60px] rounded-full opacity-20 transition-opacity group-hover:opacity-40 ${config.bg.split(' ')[0]}`} />
      
      <div className="flex items-start justify-between relative z-10 mb-4">
        <div>
          <div className="text-[10px] font-bold text-dark-400 uppercase tracking-widest mb-0.5">
            Overall Assessment
          </div>
          <div className={`text-3xl font-black tracking-tighter ${config.textClass}`}>
            {level.toUpperCase()}
          </div>
        </div>
        <div className={`p-2.5 rounded-xl ${config.bg.split(' ')[0]} bg-opacity-20`}>
          <Icon className={`w-8 h-8 ${config.color}`} />
        </div>
      </div>

      {metrics && (
        <div className="flex items-center gap-3 relative z-10 mt-auto pt-4 border-t border-white/5">
          <div className="flex-1 flex flex-col items-center p-2 rounded-lg bg-dark-950/40 border border-white/5">
            <CheckCircle2 className="w-3.5 h-3.5 text-success-500 mb-1" />
            <span className="text-xs font-bold text-white font-mono">{metrics.pass}</span>
            <span className="text-[9px] uppercase tracking-wider text-dark-400">Pass</span>
          </div>
          <div className="flex-1 flex flex-col items-center p-2 rounded-lg bg-dark-950/40 border border-white/5">
            <AlertTriangle className="w-3.5 h-3.5 text-warning-500 mb-1" />
            <span className="text-xs font-bold text-white font-mono">{metrics.warning}</span>
            <span className="text-[9px] uppercase tracking-wider text-dark-400">Warn</span>
          </div>
          <div className="flex-1 flex flex-col items-center p-2 rounded-lg bg-dark-950/40 border border-white/5">
            <AlertOctagon className="w-3.5 h-3.5 text-danger-500 mb-1" />
            <span className="text-xs font-bold text-white font-mono">{metrics.fail}</span>
            <span className="text-[9px] uppercase tracking-wider text-dark-400">Fail</span>
          </div>
        </div>
      )}
    </div>
  );
}
