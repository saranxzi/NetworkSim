import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass(slots=True)
class ChaosEvent:
    action: str              # 'kill'
    target: str              # node_id
    tick: int                # when to trigger

@dataclass(slots=True)
class InvariantRule:
    name: str
    target: str              # node_id or '*' for all nodes
    rule: str                # expression like 'latency < 150' or 'drop_rate == 0'
    severity: str = 'warning'  # 'critical' or 'warning'
    trigger_event: Optional[ChaosEvent] = None

@dataclass(slots=True)
class InvariantConfig:
    version: str = '1.0'
    scenario: str = 'Unnamed Scenario'
    duration_ticks: int = 60
    load_profile: Dict[str, Any] = field(default_factory=dict)
    invariants: List[InvariantRule] = field(default_factory=list)

def load_invariants(path: str) -> InvariantConfig:
    """Load invariant rules from a YAML file."""
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    rules = []
    for r in data.get('invariants', []):
        trigger = None
        if 'trigger_event' in r:
            te = r['trigger_event']
            trigger = ChaosEvent(
                action=te.get('action', 'kill'),
                target=te.get('target', ''),
                tick=te.get('tick', 0)
            )
        rules.append(InvariantRule(
            name=r['name'],
            target=r['target'],
            rule=r['rule'],
            severity=r.get('severity', 'warning'),
            trigger_event=trigger
        ))
    
    return InvariantConfig(
        version=data.get('version', '1.0'),
        scenario=data.get('scenario', 'Unnamed'),
        duration_ticks=data.get('duration_ticks', 60),
        load_profile=data.get('load_profile', {}),
        invariants=rules
    )
