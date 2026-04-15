from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Literal

class BaseNodeData(BaseModel):
    label: str
    type: Literal["client", "load_balancer", "api_server", "cache", "database", "message_queue", "cdn", "dns", "object_store", "serverless", "worker"]
    status: Literal["healthy", "warning", "critical", "failed"] = "healthy"
    throughput: float = 0.0
    latency: float = 0.0
    queue_depth: int = 0
    drop_rate: float = 0.0
    # Common capacities
    capacity: Optional[float] = None
    write_capacity: Optional[float] = None
    base_rps: Optional[float] = None
    base_latency: Optional[float] = None
    
class ClientData(BaseNodeData):
    type: Literal["client"] = "client"
    base_rps: float = 100.0
    burst_factor: float = 1.0

class LoadBalancerData(BaseNodeData):
    type: Literal["load_balancer"] = "load_balancer"
    algorithm: str = "round_robin"
    capacity: float = 10000.0

class ApiServerData(BaseNodeData):
    type: Literal["api_server"] = "api_server"
    capacity: float = 1000.0
    base_latency: float = 20.0 # ms

class CacheData(BaseNodeData):
    type: Literal["cache"] = "cache"
    hit_rate: float = 0.8
    capacity: float = 5000.0

class DatabaseData(BaseNodeData):
    type: Literal["database"] = "database"
    write_capacity: float = 500.0
    read_capacity: float = 2000.0
    base_latency: float = 50.0

class MessageQueueData(BaseNodeData):
    type: Literal["message_queue"] = "message_queue"
    max_depth: int = 100000
    consumers: int = 3
    throughput_per_consumer: float = 200.0

class CdnData(BaseNodeData):
    type: Literal["cdn"] = "cdn"
    capacity: float = 20000.0

class DnsData(BaseNodeData):
    type: Literal["dns"] = "dns"
    capacity: float = 50000.0

class ObjectStoreData(BaseNodeData):
    type: Literal["object_store"] = "object_store"
    capacity: float = 5000.0

class ServerlessData(BaseNodeData):
    type: Literal["serverless"] = "serverless"
    capacity: float = 10000.0 # High burstability

class WorkerData(BaseNodeData):
    type: Literal["worker"] = "worker"
    capacity: float = 500.0

class Edge(BaseModel):
    source: str
    target: str

class CanvasGraph(BaseModel):
    nodes: Dict[str, BaseNodeData]
    edges: List[Edge]

class SimulationTickResult(BaseModel):
    tick: int
    nodes: Dict[str, BaseNodeData]
    events: List[str]

class SimulationRequest(BaseModel):
    graph: CanvasGraph
    duration_ticks: int = 60
    failures_injected: List[Dict[str, Any]] = Field(default_factory=list)

class ExplanationOutput(BaseModel):
    primary_bottleneck: Optional[str] = None
    cascade_path: List[str] = Field(default_factory=list)
    narrative: str
    recommendations: List[str] = Field(default_factory=list)

class SimulationResponse(BaseModel):
    history: List[SimulationTickResult]
    explanation: ExplanationOutput
