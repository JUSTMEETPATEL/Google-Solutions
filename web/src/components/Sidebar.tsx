/** Sidebar — session history list (WEB-01). */

import { useAppStore } from '../store/appStore';
import { ShieldCheck, History, Activity, Database } from 'lucide-react';

const RISK_COLORS: Record<string, string> = {
  high: 'text-danger-500 border-danger-500/20 bg-danger-500/5',
  medium: 'text-warning-500 border-warning-500/20 bg-warning-500/5',
  low: 'text-success-500 border-success-500/20 bg-success-500/5',
};

export function Sidebar() {
  const { sessions, selectedSessionId, setSelectedSession } = useAppStore();

  return (
    <aside className="w-[260px] min-h-screen flex flex-col shrink-0 border-r border-white/5 bg-dark-950/80 backdrop-blur-3xl relative z-10 shadow-[4px_0_24px_-4px_rgba(0,0,0,0.5)]">
      {/* Sleek Header */}
      <div className="p-5 border-b border-white/5 flex flex-col items-start gap-1">
        <h1 className="text-lg font-bold text-white flex items-center gap-2.5 tracking-tight">
          <ShieldCheck className="w-5 h-5 text-primary-500" />
          FairCheck
        </h1>
        <p className="text-[10px] uppercase tracking-widest text-dark-400 font-bold ml-7">
          Audit Engine
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1 mt-2">
        <div className="px-3 mb-2 flex items-center gap-2">
          <History className="w-3.5 h-3.5 text-dark-500" />
          <h3 className="text-[10px] font-bold text-dark-500 uppercase tracking-widest">
            Audit Log
          </h3>
        </div>

        {sessions.length === 0 && (
          <div className="mt-4 px-4 py-8 rounded-xl border border-white/5 bg-dark-900/50 flex flex-col items-center text-center gap-3">
            <Database className="w-6 h-6 text-dark-600" />
            <p className="text-xs text-dark-400 font-medium">No audits found.</p>
          </div>
        )}
        
        {sessions.map((s) => {
          const isSelected = selectedSessionId === s.id;
          const riskStyle = RISK_COLORS[s.risk_level?.toLowerCase()] || 'text-dark-400 border-white/5';
          
          return (
            <button
              key={s.id}
              onClick={() => setSelectedSession(s.id)}
              className={`w-full p-3 rounded-lg border text-left transition-all duration-200 group flex flex-col gap-1.5 ${
                isSelected 
                  ? 'bg-dark-800 border-white/10 shadow-[inset_1px_1px_0_0_rgba(255,255,255,0.05),0_4px_12px_0_rgba(0,0,0,0.2)]' 
                  : 'bg-transparent border-transparent hover:bg-white/5'
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <div className={`text-sm font-semibold truncate transition-colors ${isSelected ? 'text-primary-100' : 'text-dark-200 group-hover:text-white'}`}>
                  {s.model_name || 'Unknown Model'}
                </div>
              </div>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-1.5 text-[10px] text-dark-400 font-mono">
                  <Activity className="w-3 h-3 opacity-70" />
                  <span>{s.created_at?.slice(0, 10) || '—'}</span>
                </div>
                {s.risk_level && (
                  <span className={`text-[9px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded border ${riskStyle}`}>
                    {s.risk_level}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
