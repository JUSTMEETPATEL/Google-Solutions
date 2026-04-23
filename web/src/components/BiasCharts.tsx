/** BiasCharts — Recharts-based bias visualization (WEB-03). */

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { BarChart3 } from 'lucide-react';

interface BiasChartsProps {
  analysisResults: Record<string, any>;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'];

export function BiasCharts({ analysisResults }: BiasChartsProps) {
  const results = analysisResults?.results || {};

  return (
    <div className="flex flex-col gap-10">
      {Object.entries(results).map(([attrName, attrData]: [string, any]) => (
        <div key={attrName} className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-bold text-white capitalize tracking-wide">
              {attrName.replace(/_/g, ' ')}
            </h3>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Metric values chart */}
            <div className="bg-dark-900/60 border border-white/5 rounded-2xl p-6 shadow-inner">
              <h4 className="text-sm font-semibold text-dark-300 mb-6 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary-500"></span>
                Fairness Metrics
              </h4>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={formatMetrics(attrData?.metrics || {})}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} angle={-25} textAnchor="end" height={60} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      contentStyle={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9', backdropFilter: 'blur(10px)', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)' }}
                    />
                    <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} maxBarSize={40} />
                    <Bar dataKey="threshold" fill="rgba(255,255,255,0.1)" radius={[6, 6, 0, 0]} maxBarSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Per-group performance */}
            <div className="bg-dark-900/60 border border-white/5 rounded-2xl p-6 shadow-inner">
              <h4 className="text-sm font-semibold text-dark-300 mb-6 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                Performance by Group
              </h4>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={formatBreakdown(attrData?.performance_breakdown || {})}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="group" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[0, 1]} axisLine={false} tickLine={false} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                      contentStyle={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9', backdropFilter: 'blur(10px)', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)' }}
                    />
                    <Legend wrapperStyle={{ fontSize: 12, paddingTop: '10px' }} iconType="circle" />
                    {['accuracy', 'precision', 'recall', 'f1'].map((m, i) => (
                      <Bar key={m} dataKey={m} fill={COLORS[i]} radius={[4, 4, 0, 0]} maxBarSize={20} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
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
