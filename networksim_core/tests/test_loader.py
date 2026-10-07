"""Tests for invariant YAML loading: valid files and malformed input."""
import pytest
from networksim.invariants.loader import load_invariants


def test_load_valid_file(tmp_path):
    path = tmp_path / "rules.yaml"
    path.write_text(
        "version: '1.0'\n"
        "scenario: Test\n"
        "duration_ticks: 30\n"
        "invariants:\n"
        "  - name: Fast\n"
        "    target: '*'\n"
        "    rule: latency < 100\n"
        "    severity: critical\n"
        "    trigger_event:\n"
        "      action: kill\n"
        "      target: api\n"
        "      tick: 5\n"
    )
    config = load_invariants(str(path))
    assert config.scenario == "Test"
    assert config.duration_ticks == 30
    assert len(config.invariants) == 1
    rule = config.invariants[0]
    assert rule.name == "Fast"
    assert rule.severity == "critical"
    assert rule.trigger_event is not None
    assert rule.trigger_event.target == "api"
    assert rule.trigger_event.tick == 5


def test_empty_file_raises_clear_error(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("")
    with pytest.raises(ValueError):
        load_invariants(str(path))


def test_rule_missing_required_field_raises_clear_error(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text(
        "invariants:\n"
        "  - target: '*'\n"
        "    rule: latency < 5\n"
    )
    with pytest.raises(ValueError):
        load_invariants(str(path))


def test_non_dict_rule_raises_clear_error(tmp_path):
    path = tmp_path / "weird.yaml"
    path.write_text("invariants:\n  - just-a-string\n")
    with pytest.raises(ValueError):
        load_invariants(str(path))
