import { create } from 'zustand';
import {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';

export type NodeData = {
  label: string;
  type: string;
  status?: "healthy" | "warning" | "critical" | "failed";
  throughput?: number;
  latency?: number;
  queue_depth?: number;
  capacity?: number;
  [key: string]: any;
};

export type AppState = {
  nodes: Node<NodeData>[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  setNodes: (nodes: Node<NodeData>[] | ((prev: Node<NodeData>[]) => Node<NodeData>[])) => void;
  setEdges: (edges: Edge[] | ((prev: Edge[]) => Edge[])) => void;
  
  unitCosts: Record<string, number>;
  setUnitCost: (type: string, cost: number) => void;
};

export const useStore = create<AppState>((set, get) => ({
  nodes: [],
  edges: [],
  unitCosts: {
    client: 0, dns: 5, cdn: 20, load_balancer: 15, api_server: 25, 
    serverless: 10, worker: 15, cache: 30, database: 50, object_store: 12, message_queue: 35
  },
  onNodesChange: (changes: NodeChange[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes) as Node<NodeData>[],
    });
  },
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection: Connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
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
  setUnitCost: (type, cost) => {
    set(state => ({
      unitCosts: { ...state.unitCosts, [type]: cost }
    }));
  }
}));
