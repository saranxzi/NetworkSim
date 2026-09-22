"use client"
import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { MonitorPlay, Server, Database, Layers, ArrowLeftRight, HardDrive, Globe, Network, Package, Zap, Cpu, type LucideIcon } from 'lucide-react';


interface BaseNodeProps {
  data: {
    label: string;
    type: string;
    status?: "healthy" | "warning" | "critical" | "failed";
    throughput?: number;
    latency?: number;
    queue_depth?: number;
    capacity?: number;
    write_capacity?: number;
    [key: string]: unknown;
  };
  icon: LucideIcon;
  colorClass: string;
}

export const BaseNode = memo(function BaseNode({ data, icon: Icon, colorClass }: BaseNodeProps) {
  // Determine health color ring
  let healthBorder = "border-gray-700/50";
  let healthGlow = "shadow-none";
  if (data.status === "warning") {
    healthBorder = "border-amber-500/80";
    healthGlow = "shadow-[0_0_15px_rgba(245,158,11,0.3)]";
  } else if (data.status === "critical") {
    healthBorder = "border-red-500/80";
    healthGlow = "shadow-[0_0_20px_rgba(239,68,68,0.5)]";
  } else if (data.status === "failed") {
    healthBorder = "border-red-700 bg-red-950/20";
    healthGlow = "shadow-[0_0_25px_rgba(220,38,38,0.7)]";
  } else if (data.status === "healthy") {
    healthBorder = "border-emerald-500/50";
    healthGlow = "shadow-[0_0_10px_rgba(16,185,129,0.1)]";
  }

  return (
    <div className={`relative flex w-48 flex-col rounded-xl border bg-black/60 p-3 text-white backdrop-blur-md transition-all duration-300 ${healthBorder} ${healthGlow}`}>
      {data.type !== "client" && (
        <Handle type="target" position={Position.Left} className="w-3 h-3 bg-gray-400 border-2 border-black" />
      )}
      
      <div className="flex items-center gap-3 border-b border-white/10 pb-2">
        <div className={`p-1.5 rounded-lg ${colorClass}`}>
          <Icon size={16} />
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="truncate text-xs font-medium text-gray-300 uppercase tracking-wider">{data.type.replace('_', ' ')}</div>
          <div className="truncate text-sm font-semibold text-white">{data.label}</div>
        </div>
      </div>
      
      <div className="mt-2 flex flex-col gap-1 text-[10px] text-gray-400">
        <div className="flex justify-between">
          <span>Throughput:</span>
          <span className="font-mono text-gray-100">{data.throughput?.toFixed(1) || 0} req/s</span>
        </div>
        <div className="flex justify-between">
          <span>Latency:</span>
          <span className="font-mono text-gray-100">{data.latency?.toFixed(1) || 0} ms</span>
        </div>
        {(data.queue_depth ?? 0) > 0 && (
          <div className="flex justify-between text-amber-400">
            <span>Queue:</span>
            <span className="font-mono">{data.queue_depth} depth</span>
          </div>
        )}
      </div>

      {data.type !== "client" && (data.capacity || data.write_capacity) && (
        <div className="mt-3 relative h-1 w-full overflow-hidden rounded-full bg-white/10">
          <div 
            className={`absolute inset-y-0 left-0 transition-all duration-500 ${data.status === "critical" ? "bg-red-500" : data.status === "warning" ? "bg-amber-500" : "bg-emerald-500"}`}
            style={{ 
              width: `${Math.min(100, Math.max(0, ((data.throughput || 0) / (data.capacity || data.write_capacity || 1)) * 100))}%` 
            }}
          />
        </div>
      )}

      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-gray-400 border-2 border-black" />
    </div>
  );
});

// Implement specific node wrappers — each wrapped in memo for render isolation
export const ClientNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={MonitorPlay} colorClass="bg-blue-500/20 text-blue-400" />);
export const LoadBalancerNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={ArrowLeftRight} colorClass="bg-purple-500/20 text-purple-400" />);
export const ApiServerNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Server} colorClass="bg-emerald-500/20 text-emerald-400" />);
export const CacheNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Layers} colorClass="bg-yellow-500/20 text-yellow-400" />);
export const DatabaseNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Database} colorClass="bg-rose-500/20 text-rose-400" />);
export const MessageQueueNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={HardDrive} colorClass="bg-cyan-500/20 text-cyan-400" />);
export const CdnNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Network} colorClass="bg-orange-500/20 text-orange-400" />);
export const DnsNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Globe} colorClass="bg-indigo-500/20 text-indigo-400" />);
export const ObjectStoreNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Package} colorClass="bg-amber-700/20 text-amber-500" />);
export const ServerlessNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Zap} colorClass="bg-yellow-400/20 text-yellow-300" />);
export const WorkerNode = memo((props: { data: BaseNodeProps['data'] }) => <BaseNode {...props} icon={Cpu} colorClass="bg-red-400/20 text-red-400" />);

ClientNode.displayName = 'ClientNode';
LoadBalancerNode.displayName = 'LoadBalancerNode';
ApiServerNode.displayName = 'ApiServerNode';
CacheNode.displayName = 'CacheNode';
DatabaseNode.displayName = 'DatabaseNode';
MessageQueueNode.displayName = 'MessageQueueNode';
CdnNode.displayName = 'CdnNode';
DnsNode.displayName = 'DnsNode';
ObjectStoreNode.displayName = 'ObjectStoreNode';
ServerlessNode.displayName = 'ServerlessNode';
WorkerNode.displayName = 'WorkerNode';

export const nodeTypes = {
  client: ClientNode,
  load_balancer: LoadBalancerNode,
  api_server: ApiServerNode,
  cache: CacheNode,
  database: DatabaseNode,
  message_queue: MessageQueueNode,
  cdn: CdnNode,
  dns: DnsNode,
  object_store: ObjectStoreNode,
  serverless: ServerlessNode,
  worker: WorkerNode,
};
