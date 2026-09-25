"use client";

import { useEffect, useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
  type Node
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useStore, type NodeData } from '@/lib/store';
import { nodeTypes } from '../nodes/CustomNodes';

function Flow() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, setNodes } = useStore();
  const { screenToFlowPosition } = useReactFlow();

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const stringData = event.dataTransfer.getData('app/reactflow');
      if (!stringData) return;
      
      const data = JSON.parse(stringData);
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const defaultCapacities: Record<string, Record<string, number>> = {
        client: { base_rps: 150 },
        load_balancer: { capacity: 5000 },
        api_server: { capacity: 1000 },
        cache: { capacity: 5000 },
        database: { write_capacity: 500, capacity: 500 },
        message_queue: { capacity: 10000 },
        cdn: { capacity: 20000 },
        dns: { capacity: 50000 },
        object_store: { capacity: 10000 },
        serverless: { capacity: 5000 },
        worker: { capacity: 500 },
      };

      const defaultData = defaultCapacities[data.type] || { capacity: 1000 };

      const newNode: Node<NodeData> = {
        id: `${data.type}_${Date.now()}`,
        type: data.type,
        position,
        data: {
          label: data.label,
          type: data.type,
          status: 'healthy',
          ...defaultData,
        },
      };

      setNodes((prev) => [...prev, newNode]);
    },
    [setNodes, screenToFlowPosition],
  );

  return (
    <div className="h-full w-full bg-[#0a0a0a]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        className="dark"
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#333" />
        <Controls className="bg-black/80 border border-gray-800 text-white fill-white" />
        <MiniMap 
          className="bg-black/80 border border-gray-800" 
          maskColor="rgba(0,0,0,0.7)" 
          nodeColor="#333" 
        />
      </ReactFlow>
    </div>
  );
}

export default function LabCanvas() {
  // Setup demo data initially
  const { setNodes, setEdges } = useStore();

  useEffect(() => {
    // E-commerce template by default
    setNodes([
      { id: 'client_1', type: 'client', position: { x: 100, y: 300 }, data: { label: 'Shoppers', type: 'client', status: 'healthy', base_rps: 150 } },
      { id: 'alb_1', type: 'load_balancer', position: { x: 400, y: 300 }, data: { label: 'ALB', type: 'load_balancer', status: 'healthy', capacity: 5000 } },
      { id: 'api_1', type: 'api_server', position: { x: 700, y: 300 }, data: { label: 'Checkout API', type: 'api_server', status: 'healthy', capacity: 200 } },
      { id: 'db_1', type: 'database', position: { x: 1000, y: 300 }, data: { label: 'Transactions DB', type: 'database', status: 'healthy', capacity: 150 } },
    ]);
    setEdges([
      { id: 'e1', source: 'client_1', target: 'alb_1', animated: true, style: { stroke: '#4b5563', strokeWidth: 2 } },
      { id: 'e2', source: 'alb_1', target: 'api_1', animated: true, style: { stroke: '#4b5563', strokeWidth: 2 } },
      { id: 'e3', source: 'api_1', target: 'db_1', animated: true, style: { stroke: '#4b5563', strokeWidth: 2 } },
    ]);
  }, [setNodes, setEdges]);

  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}
