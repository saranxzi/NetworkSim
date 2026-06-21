import { create } from 'zustand';
import {
  Edge,
  Node,
  EdgeChange,
  NodeChange,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';

export interface NodeData {
  label: string;
  type: string;
  status?: string;
  throughput?: number;
  latency?: number;
  queue_depth?: number;
  drop_rate?: number;
  capacity?: number;
  write_capacity?: number;
  base_rps?: number;
  base_latency?: number;
  burst_factor?: number;
  [key: string]: unknown;
}

export interface TelemetryTick {
  tick: number;
  events: string[];
  totalThroughput: number;
  totalQueue: number;
  totalDropped: number;
  nodes?: Record<string, Record<string, unknown>>;
  raw?: Record<string, unknown>;
}

export interface InvariantViolation {
  tick: number;
  ruleName: string;
  target: string;
  severity: 'critical' | 'warning';
  actualValues: Record<string, unknown>;
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
  setUnitCosts: (costs: Record<string, number>) => void;
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
  clear: () => void; // alias for clearTelemetry

  // --- Plugins ---
  plugins: Record<string, string>;
  setPlugin: (nodeType: string, code: string) => void;
  removePlugin: (nodeType: string) => void;
  clearAllPlugins: () => void;
  getPlugin: (nodeType: string) => string | undefined;

  // --- Invariant Violations ---
  violations: InvariantViolation[];
  addViolation: (v: InvariantViolation) => void;
  clearViolations: () => void;
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
  setUnitCosts: (costs) => {
    set({ unitCosts: costs });
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
            data: { ...node.data, ...delta[node.id] }
          };
        }
        return node;
      });
      if (hasChanges) {
        return { nodes: newNodes };
      }
      return state;
    });
  },

  // --- Telemetry & Simulation ---
  isRunning: false,
  buffer: [],
  rawHistory: [],
  maxBufferSize: 600,
  setRunning: (running) => set({ isRunning: running }),
  pushTick: (raw) => {
    const tickData = raw as {
      tick: number;
      events?: string[];
      nodes?: Record<string, {
        throughput?: number;
        queue_depth?: number;
        drop_rate?: number;
      }>;
    };
    
    let totalThroughput = 0;
    let totalQueue = 0;
    let totalDropped = 0;
    
    if (tickData.nodes) {
      Object.values(tickData.nodes).forEach(n => {
        totalThroughput += n.throughput || 0;
        totalQueue += n.queue_depth || 0;
        totalDropped += n.drop_rate || 0;
      });
    }

    const newTick: TelemetryTick = {
      tick: tickData.tick || 0,
      events: tickData.events || [],
      totalThroughput,
      totalQueue,
      totalDropped,
      raw
    };

    set((state) => {
      const newBuffer = [...state.buffer, newTick];
      if (newBuffer.length > state.maxBufferSize) {
        newBuffer.shift();
      }
      const newRaw = [...state.rawHistory, raw];
      if (newRaw.length > state.maxBufferSize) {
        newRaw.shift();
      }
      return { buffer: newBuffer, rawHistory: newRaw };
    });
  },
  clearTelemetry: () => set({ buffer: [], rawHistory: [] }),
  clear: () => set({ buffer: [], rawHistory: [] }),

  // --- Plugins ---
  plugins: {},
  setPlugin: (nodeType, code) => set((state) => ({
    plugins: { ...state.plugins, [nodeType]: code }
  })),
  removePlugin: (nodeType) => set((state) => {
    const next = { ...state.plugins };
    delete next[nodeType];
    return { plugins: next };
  }),
  clearAllPlugins: () => set({ plugins: {} }),
  getPlugin: (nodeType) => get().plugins[nodeType],

  // --- Invariants ---
  violations: [],
  addViolation: (v) => set((state) => ({ violations: [...state.violations, v] })),
  clearViolations: () => set({ violations: [] })
}));

// Compatibility aliases
export const useCanvasStore = useStore;
export const useTelemetryStore = useStore;
export const usePluginStore = useStore;
export const useInvariantStore = useStore;
export type CanvasStore = StoreState;
export type TelemetryStore = StoreState;
