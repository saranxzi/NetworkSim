"use client";

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface AnalyticsPanelProps {
  history: any[];
}

export default function AnalyticsPanel({ history }: AnalyticsPanelProps) {
  const chartData = useMemo(() => {
    if (!history) return [];
    
    return history.map(tick => {
      let totalThroughput = 0;
      let totalQueue = 0;
      let totalDropped = 0;
      
      const nodes = Object.values(tick.nodes) as any[];
      nodes.forEach(n => {
        totalThroughput += n.throughput || 0;
        totalQueue += n.queue_depth || 0;
        totalDropped += n.drop_rate || 0;
      });
      
      return {
        tick: tick.tick,
        Throughput: Math.round(totalThroughput),
        QueueDepth: totalQueue,
        Dropped: totalDropped
      };
    });
  }, [history]);

  const cumulativeDropped = useMemo(() => chartData.reduce((acc, curr) => acc + curr.Dropped, 0), [chartData]);
  const isCompromised = cumulativeDropped > 0;

  if (!history || history.length === 0) {
    return (
      <div className="flex h-48 w-full items-center justify-center border-t border-white/10 bg-black/60 backdrop-blur">
        <span className="text-xs text-gray-600 font-mono tracking-widest uppercase">Waiting for telemetry...</span>
      </div>
    );
  }

  return (
    <div className="h-48 w-full border-t border-white/10 bg-black/80 backdrop-blur p-4 relative overflow-hidden flex shadow-[0_-15px_30px_rgba(0,0,0,0.5)]">
      <div className="w-48 border-r border-white/10 pr-4 flex flex-col justify-center">
        <h3 className="text-xs font-semibold uppercase text-gray-500 tracking-wider mb-4">Live Telemetry</h3>
        
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-gray-400">Total Throughput</span>
          <span className="text-xs font-mono text-emerald-400">{chartData[chartData.length - 1]?.Throughput.toLocaleString()} rps</span>
        </div>
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs text-gray-400">Total Backlog</span>
          <span className="text-xs font-mono text-amber-400">{chartData[chartData.length - 1]?.QueueDepth.toLocaleString()} reqs</span>
        </div>
        
        <div className="mt-auto border-t border-white/10 pt-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Grid Status</span>
            <span className={`text-[10px] font-bold uppercase tracking-wider ${isCompromised ? 'text-red-500' : 'text-emerald-500'}`}>
               {isCompromised ? 'Compromised' : 'Flawless'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-gray-500 tracking-wider">Total Data Lost</span>
            <span className={`text-[10px] font-mono font-semibold ${isCompromised ? 'text-red-400' : 'text-gray-400'}`}>
               {cumulativeDropped.toLocaleString()} packets
            </span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 pl-4 h-full min-w-0 min-h-0">
        <ResponsiveContainer width="99%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
            <XAxis dataKey="tick" stroke="#686868" fontSize={10} tickMargin={10} />
            <YAxis stroke="#686868" fontSize={10} width={40} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
              itemStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
              labelStyle={{ color: '#888', fontSize: '11px', marginBottom: '4px' }}
            />
            <Legend wrapperStyle={{ fontSize: '10px' }} />
            <Line type="step" dataKey="Throughput" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="QueueDepth" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="step" dataKey="Dropped" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
