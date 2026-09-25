"use client";

import React, { memo, useEffect, useRef, useMemo } from 'react';
import { Terminal, AlertTriangle, Zap } from 'lucide-react';

export interface EventConsoleProps {
  history: Record<string, unknown>[];
}

interface LogEntry {
  tick: number;
  rawMsg: string;
  recommendation: string;
  type: string;
}

function getLogEntry(tick: number, evt: string): LogEntry {
  let rec = "";
  let type = "info";

  if (evt.includes("Capacity exceeded")) {
    rec = "Autoscale node capacity or attach an upstream Message Queue / Cache.";
    type = "warning";
  } else if (evt.includes("Injected failure") || evt.includes("simulated fault")) {
    rec = "Verify circuit breaker triggers and traffic reroutes to fallback paths.";
    type = "chaos";
  } else if (evt.includes("Chaos strike")) {
    rec = "Chaos monkey struck! Ensure redundancy/failover replicas are provisioned.";
    type = "chaos";
  } else if (evt.includes("Recovery")) {
    rec = "Node healthy again. Backlog is draining.";
    type = "info";
  } else {
    rec = "Normal system event.";
    type = "info";
  }

  return {
    tick,
    rawMsg: evt,
    recommendation: rec,
    type
  };
}

const EventConsole = memo(function EventConsole({ history }: EventConsoleProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const logStream = useMemo(() => {
    const logs: LogEntry[] = [];
    (history || []).forEach(tickObj => {
      const events = Array.isArray(tickObj.events) ? (tickObj.events as string[]) : [];
      const tick = typeof tickObj.tick === 'number' ? tickObj.tick : 0;
      events.forEach((evt: string) => {
        logs.push(getLogEntry(tick, evt));
      });
    });
    // Keep last 200 logs to prevent unbounded DOM growth
    return logs.slice(-200);
  }, [history]);

  // Auto-scroll to bottom of logs
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logStream.length]);

  return (
    <div className="flex flex-col flex-1 border border-white/10 bg-black/60 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)] mt-4">
      <div className="flex items-center gap-2 bg-black/80 border-b border-white/10 p-3">
        <Terminal size={14} className="text-gray-400" />
        <h3 className="text-xs font-mono font-bold tracking-widest text-gray-300 uppercase">Live Event Console</h3>
        <div className="ml-auto flex items-center gap-2">
           <span className="relative flex h-2 w-2">
             {history.length > 0 && history.length < 60 && (
               <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
             )}
             <span className={`relative inline-flex rounded-full h-2 w-2 ${history.length > 0 && history.length < 60 ? 'bg-emerald-500' : 'bg-gray-600'}`}></span>
           </span>
           <span className="text-[10px] uppercase text-gray-500 font-mono tracking-wider">{history.length > 0 && history.length < 60 ? 'Streaming' : 'Idle'}</span>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 font-mono text-xs">
        {logStream.length === 0 ? (
          <div className="text-gray-600 italic text-center mt-auto mb-auto">Awaiting telemetry...</div>
        ) : (
          logStream.map((log, i) => (
            <div key={`${log.tick}-${i}-${log.rawMsg}`} className="flex flex-col gap-1 border-l-2 pl-3 border-white/5 pb-2 border-b border-b-transparent relative group transition-colors hover:bg-white/5 py-1 -ml-3 px-3">
              <div className="flex items-start gap-2">
                <span className="text-gray-500 shrink-0 select-none">[{String(log.tick).padStart(2, '0')}]</span>
                <span className={`flex-1 break-words font-semibold 
                  ${log.type === 'chaos' ? 'text-purple-400' : 
                    log.type === 'error' ? 'text-red-400' : 
                    log.type === 'warning' ? 'text-amber-400' : 'text-blue-400'
                  }`}
                >
                  {log.type === 'chaos' && <Zap size={10} className="inline mr-1 mb-[2px]" />}
                  {log.type === 'error' && <AlertTriangle size={10} className="inline mr-1 mb-[2px]" />}
                  {log.rawMsg}
                </span>
              </div>
              <div className="flex items-start gap-2 text-gray-500 pl-[34px]">
                <span className="text-emerald-500/70 select-none">↳</span>
                <span className="text-[10px] text-gray-400 font-sans tracking-wide">
                  <span className="font-semibold mr-1 uppercase text-gray-500">Fix:</span>
                  {log.recommendation}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
});

export default EventConsole;
