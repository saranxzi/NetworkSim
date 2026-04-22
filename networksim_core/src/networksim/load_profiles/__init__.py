"""Programmable traffic load profile generators."""
from networksim.load_profiles.profiles import ramp_profile, spike_profile, diurnal_profile, soak_profile

__all__ = ["ramp_profile", "spike_profile", "diurnal_profile", "soak_profile"]
