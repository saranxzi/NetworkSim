import pytest
from networksim.invariants.checker import InvariantChecker, Violation
from networksim.invariants.loader import InvariantRule
from networksim.invariants.reporter import generate_junit_xml, generate_markdown_report

def test_passing_invariants():
    rules = [
        InvariantRule(name="Low Latency", target="*", rule="latency < 100", severity="critical")
    ]
    checker = InvariantChecker(rules)
    nodes = {"api": {"latency": 50, "throughput": 100, "queue_depth": 0, "drop_rate": 0, "status": "healthy"}}
    checker.evaluate_tick(0, nodes)
    assert checker.passed
    assert len(checker.violations) == 0

def test_failing_invariants():
    rules = [
        InvariantRule(name="Low Latency", target="*", rule="latency < 100", severity="critical")
    ]
    checker = InvariantChecker(rules)
    nodes = {"api": {"latency": 200, "throughput": 100, "queue_depth": 500, "drop_rate": 50, "status": "critical"}}
    checker.evaluate_tick(0, nodes)
    assert not checker.passed
    assert checker.has_critical_violations
    assert len(checker.violations) == 1
    assert checker.violations[0].rule_name == "Low Latency"

def test_wildcard_target():
    rules = [
        InvariantRule(name="No Drops", target="*", rule="drop_rate == 0", severity="warning")
    ]
    checker = InvariantChecker(rules)
    nodes = {
        "api": {"drop_rate": 0, "latency": 10, "throughput": 100, "queue_depth": 0, "status": "healthy"},
        "db": {"drop_rate": 50, "latency": 100, "throughput": 50, "queue_depth": 200, "status": "critical"}
    }
    checker.evaluate_tick(0, nodes)
    assert len(checker.violations) == 1
    assert checker.violations[0].target == "db"

def test_junit_output():
    violations = [
        Violation(tick=5, rule_name="Test Rule", target="api", severity="critical", expression="latency < 100", actual_values={"latency": 200})
    ]
    xml = generate_junit_xml(violations, "Test Scenario", 60, 1.5)
    assert '<?xml' in xml
    assert 'Test Rule' in xml
    assert 'failures="1"' in xml

def test_markdown_output():
    violations = [
        Violation(tick=5, rule_name="Test Rule", target="api", severity="critical", expression="latency < 100", actual_values={"latency": 200})
    ]
    md = generate_markdown_report(violations, "Test Scenario", 60, 1.5)
    assert 'FAILED' in md
    assert 'Test Rule' in md
    assert '| 5 |' in md
