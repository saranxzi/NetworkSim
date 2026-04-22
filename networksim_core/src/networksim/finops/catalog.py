from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass(slots=True)
class PricingEntry:
    provider: str
    resource_type: str
    region: str
    hourly_cost_usd: float
    capacity_rps: float
    egress_cost_per_gb: float

# Mapping of (provider, resource_type, region) to PricingEntry
CATALOG: Dict[Tuple[str, str, str], PricingEntry] = {
    # AWS
    ("aws", "api_server", "us-east-1"): PricingEntry("aws", "api_server", "us-east-1", 0.136, 1500.0, 0.09),
    ("aws", "database", "us-east-1"): PricingEntry("aws", "database", "us-east-1", 0.28, 3000.0, 0.09),
    ("aws", "cache", "us-east-1"): PricingEntry("aws", "cache", "us-east-1", 0.10, 5000.0, 0.09),
    ("aws", "load_balancer", "us-east-1"): PricingEntry("aws", "load_balancer", "us-east-1", 0.0225, 10000.0, 0.008),
    ("aws", "cdn", "us-east-1"): PricingEntry("aws", "cdn", "us-east-1", 0.015, 20000.0, 0.085),
    ("aws", "message_queue", "us-east-1"): PricingEntry("aws", "message_queue", "us-east-1", 0.40, 5000.0, 0.09),
    
    # GCP
    ("gcp", "api_server", "us-central1"): PricingEntry("gcp", "api_server", "us-central1", 0.134, 1500.0, 0.085),
    ("gcp", "database", "us-central1"): PricingEntry("gcp", "database", "us-central1", 0.29, 3000.0, 0.085),
    ("gcp", "cache", "us-central1"): PricingEntry("gcp", "cache", "us-central1", 0.11, 5000.0, 0.085),
    ("gcp", "load_balancer", "us-central1"): PricingEntry("gcp", "load_balancer", "us-central1", 0.025, 10000.0, 0.008),
    ("gcp", "cdn", "us-central1"): PricingEntry("gcp", "cdn", "us-central1", 0.016, 20000.0, 0.08),
    ("gcp", "message_queue", "us-central1"): PricingEntry("gcp", "message_queue", "us-central1", 0.42, 5000.0, 0.085),
    
    # Azure
    ("azure", "api_server", "eastus"): PricingEntry("azure", "api_server", "eastus", 0.14, 1500.0, 0.087),
    ("azure", "database", "eastus"): PricingEntry("azure", "database", "eastus", 0.27, 3000.0, 0.087),
    ("azure", "cache", "eastus"): PricingEntry("azure", "cache", "eastus", 0.12, 5000.0, 0.087),
    ("azure", "load_balancer", "eastus"): PricingEntry("azure", "load_balancer", "eastus", 0.024, 10000.0, 0.008),
    ("azure", "cdn", "eastus"): PricingEntry("azure", "cdn", "eastus", 0.017, 20000.0, 0.081),
    ("azure", "message_queue", "eastus"): PricingEntry("azure", "message_queue", "eastus", 0.39, 5000.0, 0.087),
}

def get_price(provider: str, resource_type: str, region: str) -> Optional[PricingEntry]:
    return CATALOG.get((provider, resource_type, region))

def list_providers() -> List[str]:
    return sorted(list(set(k[0] for k in CATALOG.keys())))

def list_regions(provider: str) -> List[str]:
    return sorted(list(set(k[2] for k in CATALOG.keys() if k[0] == provider)))
