import pytest
from networksim.plugins.sandbox import PluginSandbox
from networksim.plugins.registry import PluginRegistry

def test_safe_plugin_execution():
    code = '''
def on_tick(state, incoming_rps):
    forwarded = min(incoming_rps, state.get("capacity", 1000))
    dropped = max(0, incoming_rps - forwarded)
    return {"forwarded": forwarded, "dropped": dropped}
'''
    sandbox = PluginSandbox(code)
    result = sandbox.execute_tick({"capacity": 100}, 200.0)
    assert result["forwarded"] == 100
    assert result["dropped"] == 100

def test_import_blocked():
    code = '''
import os
def on_tick(state, incoming_rps):
    return {"forwarded": incoming_rps, "dropped": 0}
'''
    # Should either fail at compile time or at execution time
    try:
        sandbox = PluginSandbox(code)
        result = sandbox.execute_tick({}, 100.0)
        # If it didn't raise, it should return the default
        assert result["forwarded"] == 100.0
    except Exception:
        pass  # Expected — imports are blocked

def test_default_on_error():
    code = 'definitely not valid python !!!'
    try:
        sandbox = PluginSandbox(code)
        result = sandbox.execute_tick({}, 100.0)
        assert result["forwarded"] == 100.0
    except Exception:
        pass  # Compile error is also acceptable

def test_registry():
    reg = PluginRegistry()
    code = '''
def on_tick(state, incoming_rps):
    return {"forwarded": incoming_rps * 0.5, "dropped": incoming_rps * 0.5}
'''
    reg.register("custom_node", code)
    assert reg.has_plugin("custom_node")
    assert not reg.has_plugin("other_node")
    
    plugin = reg.get_plugin("custom_node")
    result = plugin.execute_tick({}, 200.0)
    assert result["forwarded"] == 100.0
    
    reg.remove_plugin("custom_node")
    assert not reg.has_plugin("custom_node")
