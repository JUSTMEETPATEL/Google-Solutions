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
    <div className={`h-full glass-panel rounded-xl p-6 flex flex-col justify-between relative overflow-hidden transition-all duration-300 ${level.toLowerCase() !== 'unknown' ? `border-t-2 border-t-[${config.color.replace('text-', 'var(--color-')}]` : ''}`}>
      
      <div className="flex items-start justify-between relative z-10 mb-6">
        <div>
          <div className="text-[10px] font-bold text-dark-400 uppercase tracking-widest mb-1 flex items-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${config.bg.split(' ')[0]}`}></span>
            Overall Assessment
          </div>
          <div className={`text-2xl font-bold tracking-tight ${config.textClass}`}>
            {level.toUpperCase()} RISK
          </div>
        </div>
        <div className={`p-2 rounded-lg ${config.bg.split(' ')[0]} bg-opacity-10 border border-white/5`}>
          <Icon className={`w-6 h-6 ${config.color}`} />
        </div>
      </div>

      {metrics && (
        <div className="flex items-center gap-3 relative z-10 mt-auto pt-4 border-t border-white/5">
          <div className="flex-1 flex flex-col items-start p-3 rounded-lg bg-dark-950/50 border border-white/5 transition-colors hover:bg-dark-900">
            <div className="flex items-center gap-1.5 mb-1 text-[10px] uppercase tracking-widest text-dark-400">
              <CheckCircle2 className="w-3 h-3 text-success-500" />
              Pass
            </div>
            <span className="text-sm font-semibold text-white font-mono">{metrics.pass}</span>
          </div>
          <div className="flex-1 flex flex-col items-start p-3 rounded-lg bg-dark-950/50 border border-white/5 transition-colors hover:bg-dark-900">
            <div className="flex items-center gap-1.5 mb-1 text-[10px] uppercase tracking-widest text-dark-400">
              <AlertTriangle className="w-3 h-3 text-warning-500" />
              Warn
            </div>
            <span className="text-sm font-semibold text-white font-mono">{metrics.warning}</span>
          </div>
          <div className="flex-1 flex flex-col items-start p-3 rounded-lg bg-dark-950/50 border border-white/5 transition-colors hover:bg-dark-900">
            <div className="flex items-center gap-1.5 mb-1 text-[10px] uppercase tracking-widest text-dark-400">
              <AlertOctagon className="w-3 h-3 text-danger-500" />
              Fail
            </div>
            <span className="text-sm font-semibold text-white font-mono">{metrics.fail}</span>
          </div>
        </div>
      )}
    </div>
  );
}
