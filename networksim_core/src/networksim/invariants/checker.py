"""Invariant rule checker with pre-validated, sandboxed expressions.

Rules are plain comparison expressions evaluated with `simpleeval` (restricted
grammar, no arbitrary attribute traversal) instead of raw `eval`.
"""
import ast
from dataclasses import dataclass
from simpleeval import simple_eval
from networksim.invariants.loader import InvariantRule


@dataclass(slots=True)
class Violation:
    tick: int
    rule_name: str
    target: str
    severity: str
    expression: str
    actual_values: dict[str, object]

class InvariantChecker:
    __slots__ = ['rules', 'violations']

    def __init__(self, rules: list[InvariantRule]):
        self.rules = rules
        self.violations: list[Violation] = []
        # Validate all rule expressions at init time: broken or unsafe rules
        # should fail loudly instead of surfacing mid-simulation.
        for rule in rules:
            try:
                parsed = ast.parse(rule.rule, mode='eval')
            except SyntaxError as e:
                raise ValueError(
                    f"Invalid expression in rule '{rule.name}': {rule.rule} — {e}"
                ) from e
            for node in ast.walk(parsed):
                if isinstance(node, ast.Attribute):
                    raise ValueError(
                        f"Unsafe expression in rule '{rule.name}': attribute access "
                        f"is not allowed — {rule.rule}"
                    )

    def evaluate_tick(self, tick: int, nodes: dict[str, dict]) -> list[Violation]:
        tick_violations = []
        for rule in self.rules:
            targets = self._resolve_targets(rule.target, nodes)
            for node_id, node_data in targets:
                context = {
                    'throughput': node_data.get('throughput', 0),
                    'latency': node_data.get('latency', 0),
                    'queue_depth': node_data.get('queue_depth', 0),
                    'drop_rate': node_data.get('drop_rate', 0),
                    'status': node_data.get('status', 'healthy'),
                    'capacity': node_data.get('capacity', 0),
                }
                try:
                    result = simple_eval(rule.rule, names=context)
                    if not result:
                        v = Violation(
                            tick=tick,
                            rule_name=rule.name,
                            target=node_id,
                            severity=rule.severity,
                            expression=rule.rule,
                            actual_values=context
                        )
                        tick_violations.append(v)
                        self.violations.append(v)
                except Exception as e:
                    v = Violation(
                        tick=tick,
                        rule_name=rule.name,
                        target=node_id,
                        severity="critical",
                        expression=f"EVAL_ERROR: {rule.rule} — {e}",
                        actual_values=context
                    )
                    tick_violations.append(v)
                    self.violations.append(v)
        return tick_violations

    def _resolve_targets(self, target: str, nodes: dict[str, dict]):
        if target == '*':
            return list(nodes.items())
        elif target in nodes:
            return [(target, nodes[target])]
        else:
            return [(nid, nd) for nid, nd in nodes.items() if target in nid]

    @property
    def has_critical_violations(self) -> bool:
        return any(v.severity == 'critical' for v in self.violations)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0
