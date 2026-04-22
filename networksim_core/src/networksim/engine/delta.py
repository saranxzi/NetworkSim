"""Delta tracking for simulation state."""
from typing import Dict, List, Any
from networksim.engine.physics import NodeState

class DeltaTracker:
    __slots__ = ['_prev_state', '_is_first']

    def __init__(self, node_ids: List[str]):
        self._prev_state: Dict[str, dict] = {}
        self._is_first = True

    def compute_delta(self, state: Dict[str, NodeState]) -> Dict[str, dict]:
        delta = {}
        for nid, node in state.items():
            current_data = {
                "label": node.label,
                "type": node.node_type,
                "capacity": node.capacity,
                "status": node.status,
                "throughput": round(node.current_rps, 1),
                "queue_depth": node.queue_depth,
                "drop_rate": round(node.drop_rate, 1),
                "latency": round(node.current_latency, 1)
            }
            if self._is_first:
                delta[nid] = current_data
                self._prev_state[nid] = current_data
            else:
                node_delta = {}
                prev = self._prev_state.get(nid, {})
                for k, v in current_data.items():
                    if prev.get(k) != v:
                        node_delta[k] = v
                if node_delta:
                    delta[nid] = node_delta
                self._prev_state[nid] = current_data
        
        self._is_first = False
        return delta
