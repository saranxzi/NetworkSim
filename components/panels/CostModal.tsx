"use client";

import React from 'react';
import { useStore } from '@/lib/store';
import { X, DollarSign, Activity } from 'lucide-react';

interface CostModalProps {
  onClose: () => void;
}

export default function CostModal({ onClose }: CostModalProps) {
  const { nodes, unitCosts, setUnitCost } = useStore();

  // Aggregate live usage
  const breakdowns: Record<string, { count: number, totalCapacity: number, costStr: string }> = {};
  let totalCost = 0;

  nodes.forEach(n => {
    if (n.type === 'client') return;
    const type = n.type || 'unknown';
    if (!breakdowns[type]) {
      breakdowns[type] = { count: 0, totalCapacity: 0, costStr: n.data.label as string };
    }
    
    breakdowns[type].count += 1;
    breakdowns[type].costStr = (n.data.label as string).split(' ')[0]; // rough label
    
    // @ts-ignore
    const cap = Number(n.data.capacity) || Number(n.data.write_capacity) || 1000;
    breakdowns[type].totalCapacity += cap;
    
    const baseCost = unitCosts[type] || 10;
    totalCost += baseCost * (cap / 1000);
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-[500px] rounded-xl border border-white/10 bg-gray-900 shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 bg-black/40 px-5 py-4">
          <div className="flex items-center gap-3">
             <DollarSign size={20} className="text-emerald-400" />
             <h2 className="text-sm font-semibold tracking-wide text-gray-100">Budget Configurator</h2>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col p-5 overflow-y-auto">
          
          {/* Summary Box */}
          <div className="mb-6 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4 text-center">
            <h3 className="text-xs font-semibold uppercase text-emerald-500/70 tracking-widest mb-1">Total Estimated Run Cost</h3>
            <div className="text-3xl font-bold font-mono text-emerald-400">${totalCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}<span className="text-base text-emerald-500/50 font-sans">/mo</span></div>
          </div>

          <p className="text-xs text-gray-400 mb-4 px-1 leading-relaxed">
            Configure the baseline AWS Unit prices ($ per 1,000 requests/sec) below. Costs scale linearly based on live node capacities across your architecture map.
          </p>

          {/* Breakdown List */}
          <div className="space-y-3">
            {Object.keys(unitCosts).map(type => {
              if (type === 'client') return null;
              
              const stats = breakdowns[type];
              const costThisType = stats ? (unitCosts[type] * (stats.totalCapacity / 1000)) : 0;
              const percent = totalCost > 0 ? ((costThisType / totalCost) * 100).toFixed(1) : 0;
              
              return (
                <div key={type} className="flex flex-col rounded-md border border-white/5 bg-black/40 p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-200 capitalize">{type.replace('_', ' ')}</span>
                    {stats ? (
                       <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                         ${costThisType.toLocaleString(undefined, { maximumFractionDigits: 0 })}/mo ({percent}%)
                       </span>
                    ) : (
                       <span className="text-xs text-gray-600 italic">Unused in topology</span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">Unit Price ($ per 1k RPS)</span>
                    <input 
                      type="number" 
                      min="0"
                      value={unitCosts[type]} 
                      onChange={e => setUnitCost(type, parseFloat(e.target.value) || 0)}
                      className="w-20 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-right focus:outline-none focus:border-emerald-500 transition-colors"
                    />
                  </div>
                  
                  {stats && (
                    <div className="mt-2 text-[10px] text-gray-500 flex justify-between">
                      <span>{stats.count} nodes deployed</span>
                      <span>{stats.totalCapacity.toLocaleString()} RPS total capacity</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </div>
  );
}
