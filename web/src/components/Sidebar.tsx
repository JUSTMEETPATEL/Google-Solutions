/** Sidebar — session history list (WEB-01). */

import { useAppStore } from '../store/appStore';
import { ShieldCheck, History, Activity, Database, Sparkles } from 'lucide-react';

const RISK_COLORS: Record<string, string> = {
  high: 'text-red-400 bg-red-400/10 border-red-400/20',
  medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
  low: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
};

export function Sidebar() {
  const { sessions, selectedSessionId, setSelectedSession } = useAppStore();

  return (
    <aside className="w-[300px] min-h-screen flex flex-col shrink-0 border-r border-white/5 bg-dark-900/40 backdrop-blur-md relative z-10">
      <div className="p-6 border-b border-white/5">
        <h1 className="text-xl font-bold text-white flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl shadow-lg shadow-primary-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          FairCheck
        </h1>
        <p className="text-xs text-dark-400 mt-3 flex items-center gap-1.5 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-primary-400" />
          AI Bias Detection Engine
        </p>
      </div>

      <div className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <History className="w-4 h-4 text-dark-400" />
          <h3 className="text-[11px] font-semibold text-dark-400 uppercase tracking-wider">
            Analysis History
          </h3>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-6 space-y-1">
        {sessions.length === 0 && (
          <div className="mx-2 p-6 rounded-2xl border border-dashed border-white/10 flex flex-col items-center justify-center text-center gap-3">
            <Database className="w-8 h-8 text-dark-600" />
            <p className="text-sm text-dark-400">No scans yet.<br/>Upload a model to start.</p>
          </div>
        )}
        {sessions.map((s) => {
          const isSelected = selectedSessionId === s.id;
          const riskStyle = RISK_COLORS[s.risk_level?.toLowerCase()] || 'text-dark-400 bg-dark-800 border-white/5';
          
          return (
            <button
              key={s.id}
              onClick={() => setSelectedSession(s.id)}
              className={`w-full p-3.5 rounded-xl border text-left transition-all duration-300 group ${
                isSelected 
                  ? 'bg-primary-500/10 border-primary-500/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]' 
                  : 'bg-transparent border-transparent hover:bg-white/5'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className={`text-sm font-medium truncate mb-1.5 transition-colors ${isSelected ? 'text-primary-100' : 'text-dark-100 group-hover:text-white'}`}>
                    {s.model_name || 'Unknown Model'}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-dark-400">
                    <Activity className="w-3.5 h-3.5" />
                    <span>{s.created_at?.slice(0, 10) || '—'}</span>
                  </div>
                </div>
                {s.risk_level && (
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border ${riskStyle}`}>
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
