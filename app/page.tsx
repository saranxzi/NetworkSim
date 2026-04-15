"use client";

import { useState, useEffect } from "react";
import LabCanvas from "@/components/canvas/LabCanvas";
import { Play, Settings2, Bug, Save, Trash2, Library, Activity, Download, Upload } from 'lucide-react';
import axios from 'axios';
import { useStore } from "@/lib/store";
import AnalyticsPanel from "@/components/panels/AnalyticsPanel";
import CostModal from "@/components/panels/CostModal";
import EventConsole from "@/components/panels/EventConsole";

export default function LabPage() {
  const { nodes, edges, setNodes, setEdges } = useStore();
  const [isRunning, setIsRunning] = useState(false);
  const [timelineData, setTimelineData] = useState<any>(null);
  const [streamHistory, setStreamHistory] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [failures, setFailures] = useState<any[]>([]);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [isChaosMode, setIsChaosMode] = useState(false);
  const [isCostModalOpen, setIsCostModalOpen] = useState(false);

  // Gamified AWS Cost Engine Component
  const calculateCost = () => {
    const { unitCosts } = useStore.getState();
    let total = 0;
    nodes.forEach(n => {
      if (n.type === 'client') return;
      const baseCost = unitCosts[n.type] || 10;
      // @ts-ignore
      const cap = Number(n.data.capacity) || Number(n.data.write_capacity) || 1000;
      total += baseCost * (cap / 1000); // Scaling cost linearly per 1k RPS
    });
    return total;
  };

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 4000);
  };

  // Fetch templates from backend on load
  useEffect(() => {
    axios.get('http://localhost:8000/templates')
      .then(res => setTemplates(res.data))
      .catch(console.error);
  }, []);

  const selectedNode = nodes.find(n => n.selected);
  const selectedEdge = edges.find(e => e.selected);

  // Load Template Logic
  const loadTemplate = (templateId: string) => {
    const tmpl = templates.find(t => t.id === templateId);
    if (!tmpl) return;
    
    const newNodes = Object.keys(tmpl.graph.nodes).map(nodeId => {
      const ndata = tmpl.graph.nodes[nodeId];
      return {
        id: nodeId,
        type: ndata.type,
        position: ndata.position || { x: 100, y: 100 },
        data: { ...ndata }
      };
    });
    
    const newEdges = tmpl.graph.edges.map((e: any, i: number) => ({
      id: `e_${i}`,
      source: e.source,
      target: e.target,
      animated: true,
      style: { stroke: '#4b5563', strokeWidth: 2 }
    }));

    setNodes(newNodes);
    setEdges(newEdges);
    setTimelineData(null);
    setFailures([]);
  };

  // Property Updater
  const updateSelectedNode = (key: string, value: any) => {
    if (!selectedNode) return;
    setNodes(nodes.map(n => {
      if (n.id === selectedNode.id) {
        return { ...n, data: { ...n.data, [key]: value } };
      }
      return n;
    }));
  };

  const deleteSelectedNode = () => {
    if (!selectedNode) return;
    setNodes(nodes.filter(n => n.id !== selectedNode.id));
    setEdges(edges.filter(e => e.source !== selectedNode.id && e.target !== selectedNode.id));
  };

  const handleResetTraffic = () => {
    setNodes(nodes.map(n => ({
      ...n,
      data: {
        ...n.data,
        status: 'healthy',
        throughput: 0,
        latency: 0,
        queue_depth: 0,
        drop_rate: 0
      }
    })));
    setTimelineData(null);
    setFailures([]);
    showToast("Traffic data reset! Topologies preserved.");
  };

  // Trigger explicit failure injections mapping to node_ids
  const injectFailure = (type: string) => {
    if (type === "db_crash") {
      const dbNode = nodes.find(n => n.type === 'database');
      if (dbNode) {
        setFailures([...failures, { node_id: dbNode.id, start_tick: 5 }]);
        showToast(`Failure injected: ${dbNode.data.label} will crash at tick 5.`);
      } else {
        showToast("Error: No database found in topology!");
      }
    } else if (type === "spike") {
      const clientNode = nodes.find(n => n.type === 'client');
      if (clientNode) {
        setNodes(nodes.map(n => n.id === clientNode.id ? { ...n, data: { ...n.data, base_rps: (n.data.base_rps as number || 100) * 3 } } : n));
        showToast(`Traffic Spike! ${clientNode.data.label} base traffic tripled!`);
      }
    }
  };

  const exportBlueprint = () => {
    const data = JSON.stringify({ nodes, edges }, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `blueprint-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Blueprint Exported Successfully!");
  };

  const importBlueprint = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        try {
          const data = JSON.parse(evt.target?.result as string);
          if (data.nodes && data.edges) {
            setNodes(data.nodes);
            setEdges(data.edges);
            showToast("Blueprint Imported!");
          }
        } catch (err) {
          showToast("Error: Invalid Blueprint JSON file");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setTimelineData(null); // Clear previous analysis
    setStreamHistory([]); // Clear graph
    try {
      const graph = {
        nodes: nodes.reduce((acc, n) => ({ ...acc, [n.id]: n.data }), {}),
        edges: edges.map(e => ({ source: e.source, target: e.target }))
      };
      
      const ws = new WebSocket('ws://localhost:8000/ws/simulate');
      const localHistory: any[] = [];
      
      ws.onopen = () => {
        ws.send(JSON.stringify({
          graph,
          duration_ticks: 60,
          failures_injected: failures,
          chaos_mode: isChaosMode
        }));
      };

      ws.onmessage = (event) => {
        const tickData = JSON.parse(event.data);
        localHistory.push(tickData);
        setStreamHistory([...localHistory]);
        
        // Visually render the tick!
        setNodes(currentNodes => currentNodes.map(n => {
          const liveProps = tickData.nodes[n.id];
          if (liveProps) {
            return { ...n, data: { ...n.data, ...liveProps } };
          }
          return n;
        }));
      };

      ws.onclose = async () => {
        // Stream finished! Get Analysis!
        try {
          const analyzeRes = await axios.post('http://localhost:8000/analyze', {
            history: localHistory,
            graph
          });
          
          setTimelineData({
            history: localHistory,
            explanation: analyzeRes.data
          });
        } catch (err) {
          console.error("Analysis Failed", err);
          showToast("Analysis Engine unreachable.");
        }
        
        // Cleanup
        setTimeout(() => {
          setIsRunning(false);
          setFailures([]); 
        }, 1000);
      };

      ws.onerror = (error) => {
        console.error("WebSocket Error:", error);
        setIsRunning(false);
        showToast("Simulation connection failed.");
      };
      
    } catch (e) {
      console.error(e);
      showToast("Simulation Initialization Failed.");
      setIsRunning(false);
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col bg-black text-gray-100 overflow-hidden font-sans dark relative">
      
      {/* Toast Notification */}
      {toastMsg && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-50 bg-gray-900 border border-emerald-500/50 text-emerald-400 px-6 py-3 rounded-lg shadow-2xl flex items-center gap-3 animate-in fade-in slide-in-from-top-5 duration-300">
          <Bug size={18} />
          <span className="text-sm font-medium">{toastMsg}</span>
        </div>
      )}

      {/* Top Navbar */}
      <header className="flex h-14 items-center justify-between border-b border-white/10 bg-black/50 px-6 backdrop-blur-md z-10">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="h-6 w-6 rounded-md border border-purple-500/50 bg-gradient-to-tr from-purple-600/80 to-blue-500/80 shadow-[0_0_10px_rgba(147,51,234,0.3)]"></div>
            <h1 className="text-sm font-semibold tracking-wide text-gray-100">SIM LAB <span className="font-light text-gray-500">v0.1.0</span></h1>
          </div>
          
          <button 
            onClick={() => setIsCostModalOpen(true)}
            className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-md hover:bg-emerald-500/20 transition-colors cursor-pointer"
          >
             <span className="text-xs text-emerald-500/70 font-medium tracking-wide">EST MONTHLY COST</span>
             <span className="text-sm font-mono font-bold text-emerald-400">${calculateCost().toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}/mo</span>
          </button>
        </div>
        
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer border border-white/10 bg-black px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors">
            <input 
              type="checkbox" 
              checked={isChaosMode} 
              onChange={e => setIsChaosMode(e.target.checked)} 
              className="accent-purple-500 w-4 h-4 cursor-pointer"
            />
            <span className={`text-xs font-semibold ${isChaosMode ? 'text-purple-400 drop-shadow-[0_0_5px_rgba(168,85,247,0.8)]' : 'text-gray-400'}`}>CHAOS DAEMON</span>
          </label>
          
          <div className="h-4 w-[1px] bg-white/10"></div>
          
          {templates.length > 0 && (
            <select 
              onChange={(e) => loadTemplate(e.target.value)} 
              className="bg-gray-900 border border-gray-700 text-sm rounded-md px-2 py-1 text-gray-200 focus:outline-none"
              defaultValue=""
            >
              <option value="" disabled>Load Blueprint...</option>
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          )}

          <div className="flex items-center gap-2 border border-white/10 p-1 rounded-lg bg-black/60">
            <button 
              onClick={exportBlueprint}
              title="Export Blueprint"
              className="p-1.5 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-emerald-400"
            >
              <Download size={14} />
            </button>
            <label 
              title="Import Blueprint"
              className="p-1.5 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-emerald-400 cursor-pointer"
            >
              <Upload size={14} />
              <input type="file" accept=".json" className="hidden" onChange={importBlueprint} />
            </label>
          </div>

          <div className="h-4 w-[1px] bg-white/10"></div>
          <button 
            onClick={handleResetTraffic}
            className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 py-1.5 px-3 text-xs font-medium transition-colors hover:bg-white/10"
          >
            Reset Network
          </button>
          <div className="h-4 w-[1px] bg-white/10"></div>
          <button 
            onClick={handleRunSimulation}
            disabled={isRunning}
            className="flex items-center gap-2 rounded-lg bg-emerald-600/90 py-1.5 px-4 text-xs font-semibold text-white shadow-[0_0_15px_rgba(16,185,129,0.4)] transition-all hover:bg-emerald-500 disabled:opacity-50"
          >
            {isRunning ? 'SIMULATING...' : <><Play fill="currentColor" size={12} /> RUN SIMULATION</>}
          </button>
        </div>
      </header>

      {/* Main Workspace Area */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Left Sidebar (Node Palette) */}
        <aside className="w-56 border-r border-white/10 bg-black/40 p-4 relative z-10 backdrop-blur flex flex-col gap-4 overflow-y-auto">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2 mt-2">Palette (Drag)</h2>
          <div className="flex flex-col gap-2">
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'client', label: 'Client Generator' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Client Generator</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'dns', label: 'DNS Server' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">DNS Server</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'cdn', label: 'CDN Edge' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">CDN Edge</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'load_balancer', label: 'Load Balancer' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Load Balancer</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'api_server', label: 'API Server' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">API Server</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'serverless', label: 'Serverless Func' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Serverless Func</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'worker', label: 'Worker Node' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Worker Node</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'cache', label: 'Redis Cache' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Redis Cache</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'database', label: 'PostgreSQL' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">PostgreSQL Node</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'object_store', label: 'Object Store' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Object Store</div>
            <div draggable onDragStart={(e) => e.dataTransfer.setData('app/reactflow', JSON.stringify({ type: 'message_queue', label: 'Message Queue' }))} className="rounded-lg border border-white/5 bg-white/5 p-2 hover:bg-white/10 cursor-grab active:cursor-grabbing transition-colors text-sm font-medium">Message Queue</div>
          </div>
        </aside>

        {/* Center Canvas */}
        <main className="relative flex-1 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900/40 via-black to-black">
          <LabCanvas />
        </main>

        {/* Right Sidebar (Properties & Failures) */}
        <aside className="w-80 border-l border-white/10 bg-black/40 p-5 relative z-10 backdrop-blur flex flex-col overflow-y-auto">

          <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-4">
             <Settings2 size={16} className="text-gray-400"/>
             <h2 className="text-sm font-medium text-gray-200">Properties</h2>
          </div>
          
          {!selectedNode && !selectedEdge ? (
            <div className="text-xs text-gray-500 italic mb-8">Select a node or connection on the canvas to configure parameters...</div>
          ) : selectedEdge ? (
            <div className="flex flex-col gap-4 mb-8">
              <div className="rounded-lg bg-white/5 border border-white/10 p-3 text-xs text-gray-300">
                <span className="font-semibold text-emerald-400">Connection</span> selected.
              </div>
              <button 
                onClick={() => setEdges(edges.filter(e => e.id !== selectedEdge.id))}
                className="mt-2 flex items-center justify-center gap-2 rounded-md border border-red-500/30 py-1.5 text-xs text-red-400 hover:bg-red-500/10 transition-colors"
              >
                <Trash2 size={14} /> Sever Connection
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-4 mb-8">
              <div>
                <label className="text-xs font-medium text-gray-400 block mb-1">Label</label>
                <input 
                  type="text" 
                  value={selectedNode?.data.label as string || ''} 
                  onChange={e => updateSelectedNode('label', e.target.value)}
                  className="w-full bg-black border border-gray-700 rounded-md px-3 py-1.5 text-sm"
                />
              </div>

              {selectedNode?.data.type === 'client' && (
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <label className="text-xs font-medium text-gray-400">Base Traffic (RPS)</label>
                    <span className="text-xs font-mono text-emerald-400">{selectedNode.data.base_rps as number || 0}</span>
                  </div>
                  <input 
                    type="range" 
                    min="10" max="25000" step="50"
                    value={selectedNode.data.base_rps as number || 10} 
                    onChange={e => updateSelectedNode('base_rps', parseFloat(e.target.value))}
                    className="w-full accent-emerald-500 mb-2 cursor-pointer"
                  />
                </div>
              )}

              {selectedNode?.data.type !== 'client' && selectedNode?.data.type !== 'database' && (
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <label className="text-xs font-medium text-gray-400">Processing Capacity (RPS)</label>
                    <span className="text-xs font-mono text-emerald-400">{selectedNode?.data.capacity as number || 0}</span>
                  </div>
                  <input 
                    type="range" 
                    min="10" max="50000" step="100"
                    value={selectedNode?.data.capacity as number || 10} 
                    onChange={e => updateSelectedNode('capacity', parseFloat(e.target.value))}
                    className="w-full accent-emerald-500 mb-2 cursor-pointer"
                  />
                </div>
              )}

              {selectedNode?.data.type === 'database' && (
                <div>
                  <div className="flex justify-between items-end mb-1">
                    <label className="text-xs font-medium text-gray-400">Write Capacity (RPS)</label>
                    <span className="text-xs font-mono text-emerald-400">{selectedNode.data.write_capacity as number || 0}</span>
                  </div>
                  <input 
                    type="range" 
                    min="10" max="15000" step="50"
                    value={selectedNode.data.write_capacity as number || 10} 
                    onChange={e => updateSelectedNode('write_capacity', parseFloat(e.target.value))}
                    className="w-full accent-emerald-500 mb-2 cursor-pointer"
                  />
                </div>
              )}
              
              {selectedNode?.data.type !== 'client' && (
                <div>
                  <label className="text-xs font-medium text-gray-400 block mb-1">Base Latency (ms)</label>
                  <input 
                    type="number" 
                    value={selectedNode?.data.base_latency as number || 10} 
                    onChange={e => updateSelectedNode('base_latency', parseFloat(e.target.value))}
                    className="w-full bg-black border border-gray-700 rounded-md px-3 py-1.5 text-sm"
                  />
                </div>
              )}

              <button 
                onClick={deleteSelectedNode}
                className="mt-2 flex items-center justify-center gap-2 rounded-md border border-red-500/30 py-1.5 text-xs text-red-400 hover:bg-red-500/10 transition-colors"
              >
                <Trash2 size={14} /> Delete Selected Node
              </button>
            </div>
          )}

          <div className="flex items-center gap-2 mb-4 border-b border-white/10 pb-4 mt-auto">
             <Bug size={16} className="text-amber-400"/>
             <h2 className="text-sm font-medium text-gray-200">Inject Failures</h2>
          </div>
          <button 
            onClick={() => injectFailure('db_crash')}
            className="mb-2 w-full rounded-md border border-red-500/30 bg-red-500/10 py-2 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/20"
          >
             {failures.length > 0 ? "Failure Queued" : "Simulate Database Crash"}
          </button>
          <button 
            onClick={() => injectFailure('spike')}
            className="w-full rounded-md border border-amber-500/30 bg-amber-500/10 py-2 text-xs font-medium text-amber-400 transition-colors hover:bg-amber-500/20"
          >
             Trigger Traffic Spike (3x)
          </button>

          {/* Real-time Console */}
          <EventConsole history={streamHistory} />

        </aside>
      </div>
      
      {/* Analytics Panel Bottom Rack */}
      <AnalyticsPanel history={streamHistory} />

      {/* Popups */}
      {isCostModalOpen && (
        <CostModal onClose={() => setIsCostModalOpen(false)} />
      )}

    </div>
  );
}
