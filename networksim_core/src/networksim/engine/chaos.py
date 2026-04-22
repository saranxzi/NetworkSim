"""Chaos engineering module."""
import random
from typing import Dict, List
from networksim.engine.physics import NodeState

class ChaosEngine:
    __slots__ = ['rng', 'interval']

    def __init__(self, rng: random.Random, interval: int = 15):
        self.rng = rng
        self.interval = interval

    def maybe_strike(self, tick: int, state: Dict[str, NodeState]) -> List[str]:
        if tick > 0 and tick % self.interval == 0:
            candidates = [nid for nid, node in state.items() if node.node_type != "client" and node.status != "failed"]
            if candidates:
                target = self.rng.choice(candidates)
                state[target].status = "failed"
                state[target].capacity = 0.0
                return [f"CHAOS DAEMON struck! {target} eradicated."]
        return []
