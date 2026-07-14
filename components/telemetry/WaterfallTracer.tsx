"use client";

import React, { memo } from 'react';
import { Activity, Clock, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';

export interface SpanData {
  span_id: string;
  name: string;
  service_name: string;
  duration_ms: number;
  status: string;
  attributes: Record<string, unknown>;
  children: SpanData[];
}

export interface TraceData {
  trace_id: string;
  total_duration_ms: number;
  root_span: SpanData;
}

export interface WaterfallTracerProps {
  trace: TraceData | null;
}

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'error':
    case 'failed':
      return 'bg-red-500 border-red-400 text-red-400';
    case 'warning':
    case 'critical':
      return 'bg-amber-500 border-amber-400 text-amber-400';
    case 'ok':
    default:
      return 'bg-emerald-500 border-emerald-400 text-emerald-400';
  }
};

const getStatusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case 'error':
    case 'failed':
      return <XCircle size={12} className="text-red-400" />;
    case 'warning':
    case 'critical':
      return <AlertTriangle size={12} className="text-amber-400" />;
    case 'ok':
    default:
      return <CheckCircle2 size={12} className="text-emerald-400" />;
  }
};

interface SpanRowProps {
  span: SpanData;
  depth: number;
  totalDuration: number;
}

const SpanRow = memo(function SpanRow({ span, depth, totalDuration }: SpanRowProps) {
  const widthPct = Math.max((span.duration_ms / totalDuration) * 100, 1);
  const statusStyles = getStatusColor(span.status);
  const [bgClass, borderClass, textClass] = statusStyles.split(' ');

  return (
    <div className="flex flex-col">
      <div 
        className="flex items-center hover:bg-white/5 py-1 border-b border-white/5 transition-colors group"
      >
        <div 
          className="flex items-center gap-2 w-1/3 min-w-[200px] shrink-0 pr-4"
          style={{ paddingLeft: `${Math.max(depth * 16 + 8, 8)}px` }}
        >
          {getStatusIcon(span.status)}
          <span className="text-xs font-mono text-gray-300 truncate" title={span.service_name}>
            {span.service_name}
          </span>
          <span className="text-[10px] text-gray-500 truncate" title={span.name}>
            {span.name}
          </span>
        </div>
        
        <div className="flex-1 flex items-center relative h-6 pr-4">
          <div 
            className={`h-4 rounded border/50 opacity-80 group-hover:opacity-100 transition-opacity flex items-center px-1 overflow-hidden ${bgClass} ${borderClass}`}
            style={{ width: `${widthPct}%`, minWidth: '4px' }}
          >
            {widthPct > 10 && (
              <span className="text-[9px] text-white/90 font-mono font-bold px-1 mix-blend-difference truncate">
                {span.duration_ms}ms
              </span>
            )}
          </div>
          {widthPct <= 10 && (
             <span className={`ml-2 text-[10px] font-mono ${textClass}`}>
               {span.duration_ms}ms
             </span>
          )}
        </div>
      </div>
      
      {span.children && span.children.length > 0 && (
        <div className="flex flex-col">
          {span.children.map(child => (
            <SpanRow 
              key={child.span_id} 
              span={child} 
              depth={depth + 1} 
              totalDuration={totalDuration} 
            />
          ))}
        </div>
      )}
    </div>
  );
});

export const WaterfallTracer = memo(function WaterfallTracer({ trace }: WaterfallTracerProps) {
  if (!trace) {
    return (
      <div className="flex flex-col h-full border border-white/10 bg-black/80 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)]">
         <div className="flex items-center gap-2 bg-black/90 border-b border-white/10 p-3">
          <Activity size={14} className="text-gray-400" />
          <h3 className="text-xs font-mono font-bold tracking-widest text-gray-300 uppercase">Distributed Trace</h3>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <span className="text-xs text-gray-600 font-mono tracking-widest uppercase">No trace data</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full border border-white/10 bg-black/80 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <div className="flex items-center gap-2 bg-black/90 border-b border-white/10 p-3">
        <Activity size={14} className="text-emerald-400" />
        <h3 className="text-xs font-mono font-bold tracking-widest text-gray-300 uppercase">Distributed Trace</h3>
        <div className="ml-auto flex items-center gap-4">
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider">Trace ID</span>
            <span className="text-xs font-mono text-gray-300">{trace.trace_id}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock size={12} className="text-gray-500" />
            <span className="text-xs font-mono text-gray-300">{trace.total_duration_ms}ms</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="min-w-[600px] flex flex-col pb-4">
          <div className="flex border-b border-white/10 bg-white/5 py-1">
            <div className="w-1/3 min-w-[200px] pl-2 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Service & Op</div>
            <div className="flex-1 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Timeline ({trace.total_duration_ms}ms total)</div>
          </div>
          <SpanRow span={trace.root_span} depth={0} totalDuration={trace.total_duration_ms} />
        </div>
      </div>
    </div>
  );
});

export default WaterfallTracer;
