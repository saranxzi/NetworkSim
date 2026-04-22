import uuid
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass(slots=True)
class Span:
    span_id: str
    name: str
    service_name: str
    duration_ms: float
    parent_span_id: Optional[str] = None
    status: str = 'ok'
    attributes: Dict[str, object] = field(default_factory=dict)
    children: List['Span'] = field(default_factory=list)

@dataclass(slots=True)
class Trace:
    trace_id: str
    root_span: Span
    total_duration_ms: float

class TraceGenerator:
    __slots__ = ['rng']
    
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()
    
    def generate_trace(self, tick: int, nodes: Dict[str, dict], topo_order: List[str], edges: List[tuple]) -> Optional[Trace]:
        """Generate a single synthetic trace representing one request lifecycle through the graph."""
        if not topo_order:
            return None
        
        trace_id = uuid.uuid4().hex[:32]
        
        # Build adjacency map
        adj: Dict[str, List[str]] = {}
        for src, tgt in edges:
            adj.setdefault(src, []).append(tgt)
        
        # Find entry points (nodes with no predecessors that are clients)
        entry_nodes = [n for n in topo_order if nodes.get(n, {}).get('type') == 'client']
        if not entry_nodes:
            entry_nodes = [topo_order[0]]
        
        root_node_id = entry_nodes[0]
        root_data = nodes.get(root_node_id, {})
        
        root_span = self._build_span_tree(root_node_id, root_data, adj, nodes, None)
        total_duration = self._calc_total_duration(root_span)
        
        return Trace(
            trace_id=trace_id,
            root_span=root_span,
            total_duration_ms=total_duration
        )
    
    def _build_span_tree(self, node_id: str, node_data: dict, adj: Dict[str, List[str]], all_nodes: Dict[str, dict], parent_id: Optional[str]) -> Span:
        span_id = uuid.uuid4().hex[:16]
        latency = node_data.get('latency', 0)
        status_val = node_data.get('status', 'healthy')
        
        span = Span(
            span_id=span_id,
            name=f"{node_data.get('type', 'unknown')}:{node_data.get('label', node_id)}",
            service_name=node_id,
            duration_ms=round(latency, 2),
            parent_span_id=parent_id,
            status='error' if status_val in ('failed', 'critical') else 'ok',
            attributes={
                'node.type': node_data.get('type', 'unknown'),
                'node.throughput': node_data.get('throughput', 0),
                'node.queue_depth': node_data.get('queue_depth', 0),
                'node.drop_rate': node_data.get('drop_rate', 0),
                'node.status': status_val,
            }
        )
        
        # Recurse into children
        children = adj.get(node_id, [])
        for child_id in children:
            child_data = all_nodes.get(child_id, {})
            child_span = self._build_span_tree(child_id, child_data, adj, all_nodes, span_id)
            span.children.append(child_span)
        
        return span
    
    def _calc_total_duration(self, span: Span) -> float:
        child_max = max((self._calc_total_duration(c) for c in span.children), default=0)
        return span.duration_ms + child_max
    
    def trace_to_dict(self, trace: Trace) -> dict:
        """Convert trace to a JSON-serializable dict."""
        return {
            'trace_id': trace.trace_id,
            'total_duration_ms': trace.total_duration_ms,
            'root_span': self._span_to_dict(trace.root_span)
        }
    
    def _span_to_dict(self, span: Span) -> dict:
        return {
            'span_id': span.span_id,
            'name': span.name,
            'service_name': span.service_name,
            'duration_ms': span.duration_ms,
            'parent_span_id': span.parent_span_id,
            'status': span.status,
            'attributes': span.attributes,
            'children': [self._span_to_dict(c) for c in span.children]
        }
