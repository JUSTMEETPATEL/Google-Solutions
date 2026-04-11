/** BiasCharts — Recharts-based bias visualization (WEB-03). */

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';

interface BiasChartsProps {
  analysisResults: Record<string, any>;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'];

export function BiasCharts({ analysisResults }: BiasChartsProps) {
  const results = analysisResults?.results || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {Object.entries(results).map(([attrName, attrData]: [string, any]) => (
        <div key={attrName}>
          <h3 style={{ fontSize: 15, fontWeight: 600, color: '#f1f5f9', marginBottom: 12, textTransform: 'capitalize' }}>
            {attrName.replace(/_/g, ' ')}
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Metric values chart */}
            <div style={{ background: '#1e293b', borderRadius: 12, padding: 16 }}>
              <h4 style={{ fontSize: 12, color: '#94a3b8', marginBottom: 12 }}>Fairness Metrics</h4>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={formatMetrics(attrData?.metrics || {})}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} angle={-25} textAnchor="end" height={60} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }}
                  />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="threshold" fill="#334155" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Per-group performance */}
            <div style={{ background: '#1e293b', borderRadius: 12, padding: 16 }}>
              <h4 style={{ fontSize: 12, color: '#94a3b8', marginBottom: 12 }}>Performance by Group</h4>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={formatBreakdown(attrData?.performance_breakdown || {})}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="group" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} domain={[0, 1]} />
                  <Tooltip
                    contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {['accuracy', 'precision', 'recall', 'f1'].map((m, i) => (
                    <Bar key={m} dataKey={m} fill={COLORS[i]} radius={[4, 4, 0, 0]} />
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
