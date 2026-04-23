/** RegulationSelector — dropdown for regulation framework (WEB-04). */
import { ShieldCheck, ChevronDown } from 'lucide-react';

const REGULATIONS = [
  { value: 'standard', label: 'Standard Audit' },
  { value: 'eu_ai_act_high', label: 'EU AI Act (High Risk)' },
  { value: 'nyc_144', label: 'NYC Local Law 144' },
  { value: 'nist_rmf', label: 'NIST AI RMF' },
  { value: 'internal', label: 'Internal Governance' },
];

interface RegulationSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function RegulationSelector({ value, onChange }: RegulationSelectorProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-1.5 text-sm font-semibold text-dark-400 whitespace-nowrap">
        <ShieldCheck className="w-4 h-4" />
        Regulation:
      </div>
      <div className="relative group">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="appearance-none bg-dark-800/80 hover:bg-dark-700/80 text-white border border-white/10 rounded-xl px-4 py-2 pr-10 text-sm font-medium cursor-pointer outline-none focus:ring-2 focus:ring-primary-500/50 transition-all shadow-sm"
        >
          {REGULATIONS.map((r) => (
            <option key={r.value} value={r.value} className="bg-dark-800 text-white">
              {r.label}
            </option>
          ))}
        </select>
        <ChevronDown className="w-4 h-4 text-dark-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none group-hover:text-white transition-colors" />
      </div>
    </div>
  );
}
