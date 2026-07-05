"use client";

import React, { useState } from 'react';
import { useStore } from '@/lib/store';
import { Code, Play, Trash2, CheckCircle2, AlertCircle, FileCode2 } from 'lucide-react';

const NODE_TYPES = [
  'client', 'load_balancer', 'api_server', 'database', 'cache', 'message_queue', 'worker'
];

const TEMPLATES = {
  rate_limiter: `# Rate Limiter Plugin (Python / RestrictedPython)
def on_tick(state, incoming_rps):
    capacity = state.get("capacity", 1000.0)
    if incoming_rps > capacity:
        dropped = incoming_rps - capacity
        return {"forwarded": capacity, "dropped": dropped}
    return {"forwarded": incoming_rps, "dropped": 0.0}
`,
  circuit_breaker: `# Circuit Breaker Plugin (Python / RestrictedPython)
def on_tick(state, incoming_rps):
    latency = state.get("latency", 0.0)
    # Trip circuit breaker if latency exceeds 500ms
    if latency > 500.0:
        return {"forwarded": 0.0, "dropped": incoming_rps}
    return {"forwarded": incoming_rps, "dropped": 0.0}
`,
  load_shedder: `# Adaptive Load Shedder Plugin
def on_tick(state, incoming_rps):
    queue = state.get("queue_depth", 0)
    # If queue is high, shed 50% of traffic proactively
    if queue > 1000:
        forwarded = incoming_rps * 0.5
        return {"forwarded": forwarded, "dropped": incoming_rps - forwarded}
    return {"forwarded": incoming_rps, "dropped": 0.0}
`
};

export default React.memo(function PluginEditor() {
  const { plugins, setPlugin, removePlugin } = useStore();
  const [selectedType, setSelectedType] = useState<string>(NODE_TYPES[0] ?? 'client');
  const [code, setCode] = useState<string>('');
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState<string>('');

  // Update local code when type changes
  React.useEffect(() => {
    setCode(plugins[selectedType] || '');
    setStatus('idle');
    setErrorMsg('');
  }, [selectedType, plugins]);

  const handleApply = () => {
    try {
      if (!code.trim()) {
        throw new Error('Plugin code cannot be empty');
      }
      if (!code.includes('def on_tick')) {
        throw new Error("Plugin must define 'def on_tick(state, incoming_rps):'");
      }
      setPlugin(selectedType, code);
      setStatus('success');
      setErrorMsg('');
      setTimeout(() => setStatus('idle'), 3000);
    } catch (e) {
      setStatus('error');
      setErrorMsg(e instanceof Error ? e.message : 'Validation Error');
    }
  };

  const handleClear = () => {
    removePlugin(selectedType);
    setCode('');
    setStatus('idle');
  };

  const insertTemplate = (templateKey: keyof typeof TEMPLATES) => {
    setCode(TEMPLATES[templateKey]);
  };

  return (
    <div className="w-[450px] h-full border-l border-white/10 bg-black/80 backdrop-blur flex flex-col shadow-[-15px_0_30px_rgba(0,0,0,0.5)]">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 bg-white/5">
        <div className="flex items-center gap-2">
          <Code size={16} className="text-amber-400" />
          <h2 className="text-sm font-semibold tracking-wide text-gray-200">Plugin Editor</h2>
        </div>
      </div>

      <div className="p-3 border-b border-white/10 bg-black/40">
        <div className="flex flex-col gap-2">
          <label className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Target Node Type</label>
          <select 
            value={selectedType}
            onChange={e => setSelectedType(e.target.value)}
            className="w-full bg-gray-900 border border-white/10 rounded px-2 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-amber-500"
          >
            {NODE_TYPES.map(t => (
              <option key={t} value={t}>{t.replace('_', ' ').toUpperCase()}</option>
            ))}
          </select>
        </div>
        
        <div className="mt-3 flex gap-2">
          <button onClick={() => insertTemplate('rate_limiter')} className="text-[10px] bg-white/5 hover:bg-white/10 border border-white/10 rounded px-2 py-1 text-gray-300 transition-colors">Rate Limiter</button>
          <button onClick={() => insertTemplate('circuit_breaker')} className="text-[10px] bg-white/5 hover:bg-white/10 border border-white/10 rounded px-2 py-1 text-gray-300 transition-colors">Circuit Breaker</button>
          <button onClick={() => insertTemplate('load_shedder')} className="text-[10px] bg-white/5 hover:bg-white/10 border border-white/10 rounded px-2 py-1 text-gray-300 transition-colors">Load Shedder</button>
        </div>
      </div>

      <div className="flex-1 flex flex-col p-3 relative">
        <div className="flex justify-between items-center mb-2">
          <span className="text-[10px] uppercase tracking-wider text-gray-500 font-bold flex items-center gap-1">
            <FileCode2 size={12}/> Custom Logic
          </span>
          {status === 'success' && <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle2 size={12}/> Compiled</span>}
          {status === 'error' && <span className="text-[10px] text-red-400 flex items-center gap-1"><AlertCircle size={12}/> Error</span>}
        </div>
        
        <textarea
          value={code}
          onChange={e => setCode(e.target.value)}
          spellCheck={false}
          className="flex-1 w-full bg-gray-950 border border-white/10 rounded-md p-3 text-[11px] font-mono text-gray-300 focus:outline-none focus:border-amber-500/50 resize-none leading-relaxed shadow-inner"
          placeholder="// Write standard JavaScript here to override default node behavior...&#10;// function process(node, incoming, children) { ... }"
        />
      </div>
      
      {status === 'error' && (
        <div className="px-3 pb-2">
           <div className="bg-red-500/10 border border-red-500/20 rounded p-2 text-xs text-red-400 font-mono break-all">
             {errorMsg}
           </div>
        </div>
      )}

      <div className="p-3 border-t border-white/10 bg-black/40 flex justify-between">
        <button 
          onClick={handleClear}
          className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-400 transition-colors px-2 py-1.5 rounded hover:bg-red-500/10"
        >
          <Trash2 size={14} /> Clear
        </button>
        <button 
          onClick={handleApply}
          className="flex items-center gap-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/30 rounded px-4 py-1.5 text-xs font-semibold transition-colors"
        >
          <Play size={14} /> Apply Plugin
        </button>
      </div>
    </div>
  );
});
