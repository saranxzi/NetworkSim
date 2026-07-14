"use client";

import React, { useState, useMemo, memo } from 'react';
import { Settings2, Play, Activity } from 'lucide-react';

export interface LoadProfileConfig {
  type: 'ramp' | 'spike' | 'diurnal' | 'soak';
  params: Record<string, number>;
}

export interface LoadProfileEditorProps {
  duration: number;
  onApply: (config: LoadProfileConfig) => void;
}

const PROFILE_DEFAULTS = {
  ramp: { start_rps: 100, peak_rps: 1000, ramp_ticks: 60 },
  spike: { base_rps: 200, spike_multiplier: 5, spike_start: 20, spike_duration: 10 },
  diurnal: { base_rps: 500, amplitude: 300, period_ticks: 60 },
  soak: { constant_rps: 800 }
};

export const LoadProfileEditor = memo(function LoadProfileEditor({ duration, onApply }: LoadProfileEditorProps) {
  const [profileType, setProfileType] = useState<keyof typeof PROFILE_DEFAULTS>('ramp');
  const [params, setParams] = useState<Record<string, number>>(PROFILE_DEFAULTS.ramp);

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newType = e.target.value as keyof typeof PROFILE_DEFAULTS;
    setProfileType(newType);
    setParams(PROFILE_DEFAULTS[newType]);
  };

  const handleParamChange = (key: string, val: string) => {
    setParams(prev => ({
      ...prev,
      [key]: parseFloat(val) || 0
    }));
  };

  const curvePoints = useMemo(() => {
    const points: [number, number][] = [];
    const ticks = duration > 0 ? duration : 100;
    
    let maxRps = 1;

    for (let t = 0; t <= ticks; t++) {
      let rps = 0;
      if (profileType === 'ramp') {
        const { start_rps = 0, peak_rps = 0, ramp_ticks = 1 } = params;
        if (t >= ramp_ticks) rps = peak_rps;
        else rps = start_rps + ((peak_rps - start_rps) * (t / ramp_ticks));
      } else if (profileType === 'spike') {
        const { base_rps = 0, spike_multiplier = 1, spike_start = 0, spike_duration = 1 } = params;
        if (t >= spike_start && t <= spike_start + spike_duration) {
          rps = base_rps * spike_multiplier;
        } else {
          rps = base_rps;
        }
      } else if (profileType === 'diurnal') {
        const { base_rps = 0, amplitude = 0, period_ticks = 1 } = params;
        rps = base_rps + amplitude * Math.sin((2 * Math.PI * t) / (period_ticks || 1));
      } else if (profileType === 'soak') {
        rps = params.constant_rps || 0;
      }
      
      if (rps < 0) rps = 0;
      if (rps > maxRps) maxRps = rps;
      
      points.push([t, rps]);
    }

    // Normalize to 0-100 coordinates for SVG
    return points.map(([t, rps]) => {
      const x = (t / ticks) * 100;
      const y = 100 - (rps / maxRps) * 100; // Invert Y
      return `${x},${y}`;
    }).join(' ');
  }, [profileType, params, duration]);

  const handleApply = () => {
    onApply({
      type: profileType,
      params
    });
  };

  return (
    <div className="flex flex-col border border-white/10 bg-black/80 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)] text-gray-300 font-mono text-xs w-full max-w-md">
      <div className="flex items-center gap-2 bg-black/90 border-b border-white/10 p-3">
        <Settings2 size={14} className="text-gray-400" />
        <h3 className="font-bold tracking-widest uppercase">Load Profile</h3>
      </div>
      
      <div className="p-4 flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Profile Type</label>
          <select 
            className="bg-black/60 border border-white/10 rounded px-2 py-1.5 outline-none focus:border-emerald-500/50"
            value={profileType}
            onChange={handleTypeChange}
          >
            <option value="ramp">Ramp (Step-Up)</option>
            <option value="spike">Spike (Thundering Herd)</option>
            <option value="diurnal">Diurnal (Sine Wave)</option>
            <option value="soak">Soak (Constant)</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {Object.keys(params).map(key => (
            <div key={key} className="flex flex-col gap-1">
              <label className="text-[10px] text-gray-500 uppercase tracking-wider truncate" title={key}>
                {key.replace('_', ' ')}
              </label>
              <input 
                type="number"
                className="bg-black/60 border border-white/10 rounded px-2 py-1 outline-none focus:border-emerald-500/50"
                value={params[key]}
                onChange={e => handleParamChange(key, e.target.value)}
              />
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-2 mt-2">
          <label className="text-[10px] text-gray-500 uppercase font-bold tracking-wider flex items-center justify-between">
            <span>Shape Preview</span>
            <Activity size={12} />
          </label>
          <div className="h-24 w-full bg-black/40 border border-white/5 rounded relative overflow-hidden flex items-end">
             <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
               <div className="border-b border-white/20 h-1/4"></div>
               <div className="border-b border-white/20 h-1/4"></div>
               <div className="border-b border-white/20 h-1/4"></div>
             </div>
             <svg width="100%" height="100%" preserveAspectRatio="none" className="overflow-visible" viewBox="0 0 100 100">
               <polyline
                 points={curvePoints}
                 fill="none"
                 stroke="#10b981"
                 strokeWidth="2"
                 vectorEffect="non-scaling-stroke"
               />
               <polygon 
                 points={`0,100 ${curvePoints} 100,100`} 
                 fill="url(#emerald-gradient)" 
                 opacity="0.2"
               />
               <defs>
                 <linearGradient id="emerald-gradient" x1="0" x2="0" y1="0" y2="1">
                   <stop offset="0%" stopColor="#10b981" stopOpacity="1" />
                   <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
                 </linearGradient>
               </defs>
             </svg>
          </div>
        </div>

        <button 
          onClick={handleApply}
          className="mt-2 flex items-center justify-center gap-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded py-2 transition-colors font-bold tracking-wider uppercase text-[10px]"
        >
          <Play size={12} />
          Apply Profile
        </button>
      </div>
    </div>
  );
});

export default LoadProfileEditor;
