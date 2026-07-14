'use client';

import React, { useState, useEffect, useRef, useCallback, memo } from 'react';
import { Play, Pause, Square, FastForward, SkipBack } from 'lucide-react';

interface ReplayControllerProps {
  history: Record<string, unknown>[];
  onInterpolatedTick: (interpolatedData: Record<string, unknown>) => void;
  isSimComplete: boolean;
}

const PLAYBACK_SPEEDS = [0.5, 1, 2, 4, 8];
const TICKS_PER_SECOND = 10;

function lerp(v0: number, v1: number, alpha: number): number {
  return v0 + (v1 - v0) * alpha;
}

function interpolateSnapshot(
  snap0: Record<string, unknown>,
  snap1: Record<string, unknown>,
  alpha: number
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  
  for (const key of Object.keys(snap0)) {
    const val0 = snap0[key];
    const val1 = snap1[key];
    
    if (typeof val0 === 'number' && typeof val1 === 'number') {
      result[key] = lerp(val0, val1, alpha);
    } else if (typeof val0 === 'object' && val0 !== null && typeof val1 === 'object' && val1 !== null) {
      result[key] = interpolateSnapshot(
        val0 as Record<string, unknown>,
        val1 as Record<string, unknown>,
        alpha
      );
    } else {
      result[key] = val0;
    }
  }
  
  return result;
}

const ReplayController = memo(function ReplayController({
  history,
  onInterpolatedTick,
  isSimComplete
}: ReplayControllerProps) {
  const [playbackState, setPlaybackState] = useState<'STOPPED' | 'PLAYING' | 'PAUSED'>('STOPPED');
  const [playbackSpeedIdx, setPlaybackSpeedIdx] = useState(1); // 1x default
  const [currentTick, setCurrentTick] = useState(0);
  
  const currentTickF = useRef(0);
  const lastTimeRef = useRef<number | null>(null);
  const reqRef = useRef<number | null>(null);
  
  const maxIdx = Math.max(0, history.length - 1);
  const playbackSpeed = PLAYBACK_SPEEDS[playbackSpeedIdx] ?? 1;

  const emitInterpolatedTick = useCallback((tickF: number) => {
    if (history.length === 0) return;
    
    const t0 = Math.floor(tickF);
    const t1 = Math.min(t0 + 1, maxIdx);
    const alpha = tickF - t0;
    
    const snap0 = history[t0];
    const snap1 = history[t1];
    
    if (!snap0) return;
    
    if (t0 === t1) {
      onInterpolatedTick(snap0);
    } else {
      onInterpolatedTick(interpolateSnapshot(snap0, snap1 || snap0, alpha));
    }
    
    setCurrentTick(t0);
  }, [history, maxIdx, onInterpolatedTick]);

  const loopRef = useRef<(time: number) => void>(() => {});

  const loop = useCallback((time: number) => {
    if (playbackState !== 'PLAYING') {
      lastTimeRef.current = null;
      return;
    }
    
    if (lastTimeRef.current !== null) {
      const deltaMs = time - lastTimeRef.current;
      currentTickF.current += (deltaMs / 1000) * TICKS_PER_SECOND * playbackSpeed;
      
      if (currentTickF.current >= maxIdx) {
        currentTickF.current = maxIdx;
        setPlaybackState('STOPPED');
        emitInterpolatedTick(currentTickF.current);
        lastTimeRef.current = null;
        return;
      }
      
      emitInterpolatedTick(currentTickF.current);
    }
    
    lastTimeRef.current = time;
    reqRef.current = requestAnimationFrame((t) => loopRef.current(t));
  }, [playbackState, maxIdx, playbackSpeed, emitInterpolatedTick]);

  useEffect(() => {
    loopRef.current = loop;
  }, [loop]);

  useEffect(() => {
    if (playbackState === 'PLAYING') {
      reqRef.current = requestAnimationFrame(loop);
    } else {
      if (reqRef.current !== null) {
        cancelAnimationFrame(reqRef.current);
        reqRef.current = null;
      }
      lastTimeRef.current = null;
    }
    return () => {
      if (reqRef.current !== null) {
        cancelAnimationFrame(reqRef.current);
      }
    };
  }, [playbackState, loop]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isSimComplete) return;
      
      if (e.code === 'Space') {
        e.preventDefault();
        setPlaybackState(prev => prev === 'PLAYING' ? 'PAUSED' : 'PLAYING');
      } else if (e.code === 'Escape') {
        setPlaybackState('STOPPED');
        currentTickF.current = 0;
        emitInterpolatedTick(0);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSimComplete, emitInterpolatedTick]);

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    currentTickF.current = val;
    emitInterpolatedTick(val);
    if (playbackState === 'PLAYING') {
      setPlaybackState('PAUSED');
    }
  };

  const handlePlayPause = () => {
    if (playbackState === 'PLAYING') {
      setPlaybackState('PAUSED');
    } else {
      if (currentTickF.current >= maxIdx) {
        currentTickF.current = 0;
      }
      setPlaybackState('PLAYING');
    }
  };

  const handleStop = () => {
    setPlaybackState('STOPPED');
    currentTickF.current = 0;
    emitInterpolatedTick(0);
  };
  
  const handleRewind = () => {
    currentTickF.current = 0;
    emitInterpolatedTick(0);
  };

  const cycleSpeed = () => {
    setPlaybackSpeedIdx((prev) => (prev + 1) % PLAYBACK_SPEEDS.length);
  };

  if (!isSimComplete) return null;

  return (
    <div className="flex items-center gap-4 bg-black/80 border border-white/10 p-2 rounded-lg text-white select-none">
      <div className="flex items-center gap-2">
        <button onClick={handleRewind} className="p-1 hover:bg-white/10 rounded" title="Rewind">
          <SkipBack size={18} />
        </button>
        <button onClick={handlePlayPause} className="p-1 hover:bg-white/10 rounded" title="Play/Pause (Space)">
          {playbackState === 'PLAYING' ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <button onClick={handleStop} className="p-1 hover:bg-white/10 rounded" title="Stop (Esc)">
          <Square size={18} />
        </button>
      </div>
      
      <div className="flex-1 flex items-center gap-3">
        <span className="text-xs font-mono min-w-[3rem] text-right">{currentTick}</span>
        <input 
          type="range" 
          min={0} 
          max={maxIdx} 
          step={0.01}
          value={currentTick}
          onChange={handleScrub}
          className="flex-1 accent-blue-500 h-1 bg-white/20 rounded-lg appearance-none cursor-pointer"
        />
        <span className="text-xs font-mono min-w-[3rem] text-left">{maxIdx}</span>
      </div>
      
      <div className="flex items-center">
        <button 
          onClick={cycleSpeed} 
          className="px-2 py-1 text-xs font-bold bg-white/10 hover:bg-white/20 rounded flex items-center gap-1"
        >
          {playbackSpeed}x
          <FastForward size={14} />
        </button>
      </div>
    </div>
  );
});

export default ReplayController;
