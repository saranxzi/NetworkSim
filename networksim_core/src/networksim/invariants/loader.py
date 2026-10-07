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
    """Load invariant rules from a YAML file.

    Raises ValueError with a clear message when the file is empty, the root is
    not a mapping, or a rule entry is malformed.
    """
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level, got {type(data).__name__}")

    raw_rules = data.get('invariants', [])
    if not isinstance(raw_rules, list):
        raise ValueError(f"{path}: 'invariants' must be a list, got {type(raw_rules).__name__}")

    rules = []
    for index, r in enumerate(raw_rules):
        if not isinstance(r, dict):
            raise ValueError(f"{path}: invariant #{index + 1} must be a mapping, got {type(r).__name__}")
        missing = [key for key in ('name', 'target', 'rule') if key not in r]
        if missing:
            raise ValueError(f"{path}: invariant #{index + 1} is missing required field(s): {', '.join(missing)}")
        trigger = None
        if 'trigger_event' in r:
            te = r['trigger_event']
            if not isinstance(te, dict):
                raise ValueError(f"{path}: invariant #{index + 1} 'trigger_event' must be a mapping, got {type(te).__name__}")
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
