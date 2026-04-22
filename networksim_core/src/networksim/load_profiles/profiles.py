"""Programmable traffic load profile generators."""
import math
from typing import Callable

def ramp_profile(start_rps: float, peak_rps: float, ramp_ticks: int) -> Callable[[int], float]:
    """
    Linear ramp then hold.
    Formula: r(t) = start_rps + (peak_rps - start_rps) * min(t/ramp_ticks, 1)
    """
    def profile(tick: int) -> float:
        if ramp_ticks <= 0:
            return peak_rps
        progress = min(tick / ramp_ticks, 1.0)
        return start_rps + (peak_rps - start_rps) * progress
    return profile

def spike_profile(base_rps: float, spike_multiplier: float, spike_start: int, spike_duration: int) -> Callable[[int], float]:
    """
    Rectangular spike.
    Formula: r(t) = base_rps * spike_multiplier if spike_start <= t < spike_start + spike_duration else base_rps
    """
    def profile(tick: int) -> float:
        if spike_start <= tick < spike_start + spike_duration:
            return base_rps * spike_multiplier
        return base_rps
    return profile

def diurnal_profile(base_rps: float, amplitude: float, period_ticks: int) -> Callable[[int], float]:
    """
    Sinusoidal wave.
    Formula: r(t) = base_rps + amplitude * sin(2 * pi * t / period_ticks)
    """
    def profile(tick: int) -> float:
        if period_ticks <= 0:
            return base_rps
        return base_rps + amplitude * math.sin(2 * math.pi * tick / period_ticks)
    return profile

def soak_profile(constant_rps: float) -> Callable[[int], float]:
    """
    Constant load.
    Formula: r(t) = constant_rps
    """
    def profile(tick: int) -> float:
        return constant_rps
    return profile
