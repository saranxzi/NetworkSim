import pytest
from networksim.finops import CostCalculator, list_providers, get_price

def test_catalog_providers():
    providers = list_providers()
    assert "aws" in providers
    assert "gcp" in providers
    assert "azure" in providers

def test_get_price_existing_and_fallback():
    entry = get_price("aws", "database", "us-east-1")
    assert entry is not None
    assert entry.hourly_cost_usd > 0
    assert entry.capacity_rps > 0

    # Non-existent node type
    entry_missing = get_price("aws", "non_existent_type", "us-east-1")
    assert entry_missing is None

def test_cost_calculator_node_and_graph():
    calc = CostCalculator()
    node_cost = calc.estimate_node_cost(
        node_type="api_server",
        provider="aws",
        region="us-east-1",
        avg_throughput_rps=500.0,
        avg_egress_gb_per_hour=1.0
    )
    assert node_cost.hourly > 0
    assert node_cost.monthly == pytest.approx(node_cost.hourly * 730)
    assert node_cost.compute > 0
    assert node_cost.egress > 0

    nodes = {
        "api1": {"type": "api_server", "throughput": 1000.0, "egress_gb": 0.5},
        "db1": {"type": "database", "throughput": 200.0, "egress_gb": 0.1},
    }
    graph_costs = calc.estimate_graph_cost(nodes, "aws", "us-east-1")
    assert "api1" in graph_costs
    assert "db1" in graph_costs

    total = calc.total_monthly_cost(graph_costs)
    assert total == pytest.approx(graph_costs["api1"].monthly + graph_costs["db1"].monthly)

def test_cost_calculator_zero_throughput_graceful():
    calc = CostCalculator()
    cost = calc.estimate_node_cost(
        node_type="api_server",
        provider="aws",
        region="us-east-1",
        avg_throughput_rps=0.0
    )
    assert cost.monthly > 0  # At least 1 base instance
