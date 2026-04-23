/** IntersectionalPanel — displays intersectional bias analysis results. */

import { Users, AlertTriangle, TrendingDown } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import type { IntersectionalAnalysis } from '../api/client';

interface IntersectionalPanelProps {
  data: IntersectionalAnalysis;
}

const COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'];
const STATUS_COLORS: Record<string, string> = {
  pass: '#22c55e',
  warning: '#eab308',
  fail: '#ef4444',
  skipped: '#6b7280',
};

export function IntersectionalPanel({ data }: IntersectionalPanelProps) {
  if (!data || !data.intersections || data.intersections.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Most disadvantaged group alert */}
      {data.most_disadvantaged && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3 animate-in fade-in duration-500">
          <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-bold text-red-400 mb-1">Most Disadvantaged Intersectional Group</p>
            <p className="text-xs text-zinc-300">
              <span className="font-mono text-red-300">{data.most_disadvantaged.group}</span>
              {' '}in the <span className="font-semibold text-white">{data.most_disadvantaged.intersection}</span> intersection
              has a predicted positive rate of only{' '}
              <span className="font-mono text-red-300">{(data.most_disadvantaged.predicted_positive_rate * 100).toFixed(1)}%</span>
              {' '}(n={data.most_disadvantaged.count}).
            </p>
          </div>
        </div>
      )}

      {/* Intersection cards */}
      {data.intersections.map((intersection, idx) => (
        <div key={intersection.intersection} className="animate-in fade-in slide-in-from-bottom-4 duration-700" style={{ animationDelay: `${idx * 100}ms` }}>
          <div className="flex items-center gap-3 mb-4 pl-2 border-l-2 border-purple-500">
            <Users className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-black text-white uppercase tracking-widest">
              {intersection.intersection}
            </h3>
            <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded">
              {intersection.n_valid_groups} groups
            </span>
          </div>

          <div className="grid lg:grid-cols-2 gap-4">
            {/* Group selection rates chart */}
            <div className="glass-panel p-4 rounded-xl h-[280px]">
              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-3">Positive Outcome Rates</h4>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={formatGroupRates(intersection.group_rates)} margin={{ top: 5, right: 10, left: -15, bottom: 30 }} barSize={14}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis
                    dataKey="group"
                    tick={{ fill: '#a1a1aa', fontSize: 9, fontFamily: 'monospace' }}
                    angle={-30}
                    textAnchor="end"
                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                    tickLine={false}
                    tickMargin={8}
                  />
                  <YAxis tick={{ fill: '#a1a1aa', fontSize: 9, fontFamily: 'monospace' }} domain={[0, 1]} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{
                      background: 'rgba(9, 9, 11, 0.95)',
                      border: '1px solid rgba(139, 92, 246, 0.3)',
                      borderRadius: '10px',
                      color: '#f1f5f9',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: 9, fontFamily: 'monospace', paddingTop: '6px' }} iconType="circle" />
                  <Bar dataKey="predicted" name="Predicted +" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="actual" name="Actual +" fill="#06b6d4" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Metrics summary for intersection */}
            <div className="glass-panel p-4 rounded-xl">
              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-3">Fairness Metrics</h4>
              <div className="flex flex-col gap-2">
                {Object.entries(intersection.metrics).map(([metricName, metricData]: [string, any]) => {
                  const status = metricData?.status || 'skipped';
                  return (
                    <div key={metricName} className="flex items-center justify-between py-2 px-3 rounded-lg bg-black/20">
                      <span className="text-xs font-mono text-zinc-300 truncate max-w-[140px]">
                        {metricName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono text-zinc-400">
                          {metricData?.value != null ? metricData.value.toFixed(4) : 'N/A'}
                        </span>
                        <span
                          className="text-[10px] font-bold uppercase px-2 py-0.5 rounded"
                          style={{
                            color: STATUS_COLORS[status],
                            backgroundColor: `${STATUS_COLORS[status]}15`,
                          }}
                        >
                          {status}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function formatGroupRates(groupRates: Record<string, any>): any[] {
  return Object.entries(groupRates).map(([group, data]) => ({
    group: group.length > 20 ? group.substring(0, 18) + '…' : group,
    predicted: data.predicted_positive_rate ?? 0,
    actual: data.actual_positive_rate ?? 0,
    count: data.count ?? 0,
  }));
}
