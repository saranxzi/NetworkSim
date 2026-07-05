"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useStore } from '@/lib/store';
import { Save, Download, Clock, Check, Server, FileJson } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface BlueprintSummary {
  id: string;
  name: string;
  updatedAt: string;
  versionCount: number;
}

interface BlueprintDetail {
  id: string;
  name: string;
  graph: {
    nodes: unknown[];
    edges: unknown[];
  };
}

export default React.memo(function BlueprintManager() {
  const { token, isAuthenticated } = useAuth();
  const { nodes, edges, setNodes, setEdges } = useStore();
  
  const [blueprints, setBlueprints] = useState<BlueprintSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [blueprintName, setBlueprintName] = useState('');
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  };

  const fetchBlueprints = async (authToken: string | null): Promise<BlueprintSummary[]> => {
    try {
      const res = await fetch(`${API_BASE}/api/blueprints`, {
        headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {}
      });
      if (!res.ok) throw new Error('Failed to fetch blueprints');
      return await res.json();
    } catch (err) {
      console.error(err);
      return [];
    }
  };

  const saveBlueprint = async (authToken: string | null, name: string, graph: object): Promise<void> => {
    const res = await fetch(`${API_BASE}/api/blueprints`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
      },
      body: JSON.stringify({ name, graph }),
    });
    if (!res.ok) throw new Error('Failed to save blueprint');
  };

  const loadBlueprint = async (authToken: string | null, id: string): Promise<BlueprintDetail> => {
    const res = await fetch(`${API_BASE}/api/blueprints/${id}`, {
      headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {}
    });
    if (!res.ok) throw new Error('Failed to load blueprint');
    return await res.json();
  };

  const loadList = async () => {
    if (!isAuthenticated && process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true') return;
    setIsLoading(true);
    const list = await fetchBlueprints(token);
    setBlueprints(list);
    setIsLoading(false);
  };

  useEffect(() => {
    loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAuthenticated]);

  const handleSave = async () => {
    if (!blueprintName.trim()) {
      showToast('Please enter a blueprint name');
      return;
    }
    
    try {
      await saveBlueprint(token, blueprintName, { nodes, edges });
      showToast('Blueprint saved successfully');
      setBlueprintName('');
      loadList();
    } catch {
      showToast('Error saving blueprint');
    }
  };

  const handleLoad = async (id: string) => {
    try {
      const detail = await loadBlueprint(token, id);
      setNodes(detail.graph.nodes as typeof nodes);
      setEdges(detail.graph.edges as typeof edges);
      showToast(`Loaded ${detail.name}`);
    } catch {
      showToast('Error loading blueprint');
    }
  };

  return (
    <div className="w-80 h-full border-l border-white/10 bg-black/80 backdrop-blur flex flex-col shadow-[-15px_0_30px_rgba(0,0,0,0.5)]">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3 bg-white/5">
        <FileJson size={16} className="text-emerald-400" />
        <h2 className="text-sm font-semibold tracking-wide text-gray-200">Blueprints</h2>
      </div>

      <div className="p-4 border-b border-white/10 bg-black/40">
        <div className="flex flex-col gap-2">
          <label className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Save Current State</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={blueprintName}
              onChange={e => setBlueprintName(e.target.value)}
              placeholder="e.g. Prod Architecture v2"
              className="flex-1 bg-gray-900 border border-white/10 rounded px-2 py-1.5 text-xs text-gray-200 placeholder-gray-600 focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button
              onClick={handleSave}
              className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 rounded p-1.5 transition-colors"
              title="Save Blueprint"
            >
              <Save size={16} />
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        <div className="px-2 pt-2 pb-1 text-[10px] uppercase tracking-wider text-gray-500 font-bold">Saved Blueprints</div>
        
        {isLoading ? (
          <div className="text-xs text-center text-gray-500 py-4">Loading...</div>
        ) : blueprints.length === 0 ? (
          <div className="text-xs text-center text-gray-600 py-4 italic">No blueprints found.</div>
        ) : (
          blueprints.map(bp => (
            <div key={bp.id} className="group flex flex-col border border-white/5 bg-gray-900/50 rounded-md p-3 hover:border-emerald-500/30 transition-colors cursor-pointer" onClick={() => handleLoad(bp.id)}>
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm text-gray-200 font-medium">{bp.name}</span>
                <button className="text-gray-500 group-hover:text-emerald-400 transition-colors opacity-0 group-hover:opacity-100">
                  <Download size={14} />
                </button>
              </div>
              <div className="flex items-center gap-3 text-[10px] text-gray-500">
                <span className="flex items-center gap-1"><Clock size={10} /> {new Date(bp.updatedAt).toLocaleDateString()}</span>
                <span className="flex items-center gap-1"><Server size={10} /> v{bp.versionCount}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {toastMsg && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-gray-800 text-xs text-white px-3 py-1.5 rounded-full shadow-lg flex items-center gap-2 border border-white/10 z-50">
          <Check size={12} className="text-emerald-400" />
          {toastMsg}
        </div>
      )}
    </div>
  );
});
