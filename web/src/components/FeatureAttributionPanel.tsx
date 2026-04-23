/** FeatureAttributionPanel — displays SHAP/permutation importance results. */

import { Layers, AlertTriangle, ArrowDownUp } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import type { FeatureAttribution, BiasDriver } from '../api/client';

interface FeatureAttributionPanelProps {
  data: FeatureAttribution;
}

export function FeatureAttributionPanel({ data }: FeatureAttributionPanelProps) {
  if (!data) return null;

  const globalData = Object.entries(data.global_importance || {})
    .slice(0, 12)
    .map(([name, vals]) => ({
      name: name.length > 18 ? name.substring(0, 16) + '…' : name,
      importance: vals.importance_mean,
      std: vals.importance_std,
    }));

  return (
    <div className="flex flex-col gap-6">
      {/* Bias Drivers Alert */}
      {data.bias_drivers && data.bias_drivers.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 animate-in fade-in duration-500">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-bold text-amber-400 uppercase tracking-widest">Bias Drivers Detected</h4>
          </div>
          <div className="flex flex-col gap-2">
            {data.bias_drivers.slice(0, 5).map((driver, i) => (
              <BiasDriverRow key={i} driver={driver} rank={i + 1} />
            ))}
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Global Feature Importance */}
        <div className="glass-panel p-5 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">
              Global Feature Importance
            </h4>
          </div>
          {globalData.length > 0 ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={globalData} layout="vertical" margin={{ top: 5, right: 20, left: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis
                    type="number"
                    tick={{ fill: '#a1a1aa', fontSize: 9, fontFamily: 'monospace' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fill: '#a1a1aa', fontSize: 9, fontFamily: 'monospace' }}
                    axisLine={false}
                    tickLine={false}
                    width={110}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{
                      background: 'rgba(9, 9, 11, 0.95)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      borderRadius: '10px',
                      color: '#f1f5f9',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                    }}
                  />
                  <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} barSize={10} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-sm text-zinc-500 italic">No feature importance data available.</p>
          )}
        </div>

        {/* Per-Group Importance Comparison */}
        <div className="glass-panel p-5 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <ArrowDownUp className="w-4 h-4 text-purple-400" />
            <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">
              Cross-Group Importance
            </h4>
          </div>
          <div className="flex flex-col gap-3 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
            {Object.entries(data.per_group_importance || {}).map(([attr, groups]) => (
              <div key={attr}>
                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">
                  {attr.replace(/_/g, ' ')}
                </p>
                <div className="flex flex-col gap-1">
                  {Object.entries(groups).map(([group, features]) => {
                    const topFeatures = Object.entries(features as Record<string, number>)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 3);
                    return (
                      <div key={group} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-black/20">
                        <span className="text-xs font-mono text-zinc-400 w-20 truncate">{group}</span>
                        <div className="flex-1 flex gap-1.5 flex-wrap">
                          {topFeatures.map(([fname, val]) => (
                            <span key={fname} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300">
                              {fname.substring(0, 12)}: {(val as number).toFixed(3)}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function BiasDriverRow({ driver, rank }: { driver: BiasDriver; rank: number }) {
  return (
    <div className="flex items-start gap-3 px-3 py-2 rounded-lg bg-black/20">
      <span className="text-xs font-bold text-amber-400 bg-amber-500/20 w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5">
        {rank}
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-zinc-300">
          <span className="font-mono font-bold text-amber-300">{driver.feature}</span>
          {' '}differs by{' '}
          <span className="font-mono text-amber-400">{(driver.importance_spread * 100).toFixed(1)}%</span>
          {' '}between groups
        </p>
        <p className="text-[10px] text-zinc-500 mt-0.5">{driver.explanation}</p>
      </div>
    </div>
  );
}
