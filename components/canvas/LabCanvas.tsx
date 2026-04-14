"use client";

import { useEffect, useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useStore } from '@/lib/store';
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

      let defaultData: any = {};
      if (data.type === 'client') defaultData = { base_rps: 150 };
      else if (data.type === 'load_balancer') defaultData = { capacity: 5000 };
      else if (data.type === 'api_server') defaultData = { capacity: 1000 };
      else if (data.type === 'cache') defaultData = { capacity: 5000 };
      else if (data.type === 'database') defaultData = { write_capacity: 500, capacity: 500 }; 
      else if (data.type === 'message_queue') defaultData = { capacity: 10000 };
      else if (data.type === 'cdn') defaultData = { capacity: 20000 };
      else if (data.type === 'dns') defaultData = { capacity: 50000 };
      else if (data.type === 'object_store') defaultData = { capacity: 10000 };
      else if (data.type === 'serverless') defaultData = { capacity: 5000 };
      else if (data.type === 'worker') defaultData = { capacity: 500 };

      const newNode = {
        id: `${data.type}_${Date.now()}`,
        type: data.type,
        position,
        data: { label: data.label, type: data.type, ...defaultData },
      };

      setNodes([...nodes, newNode as any]);
    },
    [nodes, setNodes, screenToFlowPosition],
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
      { id: 'client_1', type: 'client', position: { x: 100, y: 300 }, data: { label: 'Shoppers', type: 'client', base_rps: 150 } },
      { id: 'alb_1', type: 'load_balancer', position: { x: 400, y: 300 }, data: { label: 'ALB', type: 'load_balancer', capacity: 5000 } },
      { id: 'api_1', type: 'api_server', position: { x: 700, y: 300 }, data: { label: 'Checkout API', type: 'api_server', capacity: 200 } },
      { id: 'db_1', type: 'database', position: { x: 1000, y: 300 }, data: { label: 'Transactions DB', type: 'database', capacity: 150 } },
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
