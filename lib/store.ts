import { create } from 'zustand';
import { Node, Edge, NodeChange, EdgeChange, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';

export interface NodeData {
  label: string;
  type: string;
  status: 'healthy' | 'warning' | 'critical' | 'failed';
  throughput?: number;
  latency?: number;
  queue_depth?: number;
  drop_rate?: number;
  capacity?: number;
  write_capacity?: number;
  base_latency?: number;
  base_rps?: number;
  burst_factor?: number;
  [key: string]: unknown;
}

export interface TelemetryTick {
  tick: number;
  timestamp: number;
  totalThroughput: number;
  totalQueue: number;
  totalDropped: number;
  nodes?: Record<string, Record<string, unknown>>;
  raw?: Record<string, unknown>;
}

export interface StoreState {
  // --- Topology ---
  nodes: Node<NodeData>[];
  edges: Edge[];
  unitCosts: Record<string, number>;
  setNodes: (nodes: Node<NodeData>[] | ((prev: Node<NodeData>[]) => Node<NodeData>[])) => void;
  setEdges: (edges: Edge[] | ((prev: Edge[]) => Edge[])) => void;
  onNodesChange: (changes: NodeChange<Node<NodeData>>[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: { source: string; target: string; sourceHandle?: string | null; targetHandle?: string | null }) => void;
  setUnitCost: (type: string, cost: number) => void;
  applyDelta: (delta: Record<string, Record<string, unknown>>) => void;

  // --- Telemetry & Simulation ---
  isRunning: boolean;
  buffer: TelemetryTick[];
  rawHistory: Record<string, unknown>[];
  maxBufferSize: number;
  setRunning: (running: boolean) => void;
  pushTick: (raw: Record<string, unknown>) => void;
  clearTelemetry: () => void;

  // --- Plugins ---
  plugins: Record<string, string>;
  setPlugin: (nodeType: string, code: string) => void;
  removePlugin: (nodeType: string) => void;
}

export const useStore = create<StoreState>((set, get) => ({
  // --- Topology ---
  nodes: [],
  edges: [],
  unitCosts: {
    client: 0, dns: 5, cdn: 20, load_balancer: 15, api_server: 25, 
    serverless: 10, worker: 15, cache: 30, database: 50, object_store: 12, message_queue: 35
  },
  setNodes: (nodesOrUpdater) => {
    set((state) => ({ 
      nodes: typeof nodesOrUpdater === 'function' ? nodesOrUpdater(state.nodes) : nodesOrUpdater 
    }));
  },
  setEdges: (edgesOrUpdater) => {
    set((state) => ({ 
      edges: typeof edgesOrUpdater === 'function' ? edgesOrUpdater(state.edges) : edgesOrUpdater 
    }));
  },
  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection) => {
    const newEdge: Edge = {
      id: `e_${connection.source}_${connection.target}_${Date.now()}`,
      source: connection.source,
      target: connection.target,
      animated: true,
      style: { stroke: '#10b981', strokeWidth: 2 },
    };
    set({ edges: [...get().edges, newEdge] });
  },
  setUnitCost: (type, cost) => {
    set((state) => ({ unitCosts: { ...state.unitCosts, [type]: cost } }));
  },
  applyDelta: (delta) => {
    set((state) => {
      let hasChanges = false;
      const newNodes = state.nodes.map((node) => {
        if (delta[node.id]) {
          hasChanges = true;
          return {
            ...node,
            data: {
              ...node.data,
              ...delta[node.id]
            }
          };
        }
        return node;
      });
      return hasChanges ? { nodes: newNodes } : state;
    });
  },

  // --- Telemetry & Simulation ---
  isRunning: false,
  buffer: [],
  rawHistory: [],
  maxBufferSize: 600,
  setRunning: (running) => set({ isRunning: running }),
  pushTick: (raw) => {
    let totalThroughput = 0;
    let totalQueue = 0;
    let totalDropped = 0;

    const rawNodes = (raw.nodes || {}) as Record<string, Record<string, unknown>>;
    Object.values(rawNodes).forEach((nodeMetrics) => {
      if (typeof nodeMetrics.throughput === 'number') totalThroughput += nodeMetrics.throughput;
      if (typeof nodeMetrics.queue_depth === 'number') totalQueue += nodeMetrics.queue_depth;
      if (typeof nodeMetrics.drop_rate === 'number') totalDropped += nodeMetrics.drop_rate;
    });

    const newTick: TelemetryTick = {
      tick: typeof raw.tick === 'number' ? raw.tick : get().buffer.length,
      timestamp: Date.now(),
      totalThroughput,
      totalQueue,
      totalDropped,
      raw
    };

    set((state) => {
      const buffer = state.buffer.length >= state.maxBufferSize
        ? [...state.buffer.slice(1), newTick]
        : [...state.buffer, newTick];
      const rawHistory = state.rawHistory.length >= state.maxBufferSize
        ? [...state.rawHistory.slice(1), raw]
        : [...state.rawHistory, raw];
      return { buffer, rawHistory };
    });
  },
  clearTelemetry: () => set({ buffer: [], rawHistory: [] }),

  // --- Plugins ---
  plugins: {},
  setPlugin: (nodeType, code) => set((state) => ({
    plugins: { ...state.plugins, [nodeType]: code }
  })),
  removePlugin: (nodeType) => set((state) => {
    const next = { ...state.plugins };
    delete next[nodeType];
    return { plugins: next };
  })
}));
