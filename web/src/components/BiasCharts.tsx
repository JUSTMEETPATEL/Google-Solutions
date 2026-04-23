/** BiasCharts — Recharts-based bias visualization (WEB-03). */

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity } from 'lucide-react';

interface BiasChartsProps {
  analysisResults: Record<string, any>;
}

const COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981'];

export function BiasCharts({ analysisResults }: BiasChartsProps) {
  const results = analysisResults?.results || {};

  if (Object.keys(results).length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 border border-white/5 rounded-2xl bg-dark-900/30 shadow-inner">
        <div className="p-4 bg-dark-800 rounded-full mb-4 shadow-[0_0_20px_rgba(0,0,0,0.5)] border border-white/5">
          <Activity className="w-8 h-8 text-primary-500 animate-pulse" />
        </div>
        <p className="text-dark-400 font-bold text-sm tracking-widest uppercase">Awaiting Metric Telemetry</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      {Object.entries(results).map(([attrName, attrData]: [string, any]) => (
        <div key={attrName} className="animate-in fade-in duration-700 slide-in-from-bottom-4">
          <div className="flex items-center gap-3 mb-5 pl-2 border-l-2 border-primary-500">
            <h3 className="text-lg font-black text-white uppercase tracking-widest drop-shadow-md">
              {attrName.replace(/_/g, ' ')}
            </h3>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Metric values chart */}
            <div className="glass-panel h-[320px] p-5 rounded-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 blur-[50px] -z-10 transition-opacity group-hover:bg-primary-500/10" />
              <h4 className="text-xs font-bold text-dark-400 uppercase tracking-widest mb-4">Core Fairness Metrics</h4>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={formatMetrics(attrData?.metrics || {})} margin={{ top: 10, right: 10, left: -20, bottom: 40 }} barSize={16}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: '#a1a1aa', fontSize: 10, fontFamily: 'monospace' }} angle={-25} textAnchor="end" axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} tickLine={false} tickMargin={10} />
                  <YAxis tick={{ fill: '#a1a1aa', fontSize: 10, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ background: 'rgba(9, 9, 11, 0.9)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '12px', color: '#f1f5f9', fontSize: '11px', fontFamily: 'monospace', backdropFilter: 'blur(10px)', boxShadow: '0 0 20px rgba(6,182,212,0.2)' }}
                  />
                  <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="threshold" fill="rgba(255,255,255,0.15)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Per-group performance */}
            <div className="glass-panel h-[320px] p-5 rounded-2xl relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-32 h-32 bg-purple-500/5 blur-[50px] -z-10 transition-opacity group-hover:bg-purple-500/10" />
              <h4 className="text-xs font-bold text-dark-400 uppercase tracking-widest mb-4">Performance Stratification</h4>
              <ResponsiveContainer width="100%" height="90%">
                <BarChart data={formatBreakdown(attrData?.performance_breakdown || {})} margin={{ top: 10, right: 10, left: -20, bottom: 20 }} barSize={10}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="group" tick={{ fill: '#a1a1aa', fontSize: 10, fontFamily: 'monospace' }} axisLine={{ stroke: 'rgba(255,255,255,0.1)' }} tickLine={false} tickMargin={10} />
                  <YAxis tick={{ fill: '#a1a1aa', fontSize: 10, fontFamily: 'monospace' }} domain={[0, 1]} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ background: 'rgba(9, 9, 11, 0.9)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: '12px', color: '#f1f5f9', fontSize: '11px', fontFamily: 'monospace', backdropFilter: 'blur(10px)', boxShadow: '0 0 20px rgba(139, 92, 246, 0.2)' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 10, fontFamily: 'monospace', paddingTop: '10px' }} iconType="circle" />
                  {['accuracy', 'precision', 'recall', 'f1'].map((m, i) => (
                    <Bar key={m} dataKey={m} fill={COLORS[i]} radius={[3, 3, 0, 0]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function formatMetrics(metrics: Record<string, any>): any[] {
  return Object.entries(metrics).map(([name, data]: [string, any]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()).slice(0, 18),
    value: data?.value ?? 0,
    threshold: data?.threshold ?? 0,
    status: data?.status ?? 'skipped',
  }));
}

function formatBreakdown(breakdown: Record<string, any>): any[] {
  return Object.entries(breakdown).map(([group, data]: [string, any]) => ({
    group,
    accuracy: data?.accuracy ?? 0,
    precision: data?.precision ?? 0,
    recall: data?.recall ?? 0,
    f1: data?.f1 ?? 0,
  }));
}
