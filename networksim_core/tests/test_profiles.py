import pytest
from networksim.load_profiles import ramp_profile, spike_profile, diurnal_profile, soak_profile

def test_ramp_profile():
    p = ramp_profile(start_rps=100.0, peak_rps=500.0, ramp_ticks=10)
    assert p(0) == 100.0
    assert p(5) == 300.0
    assert p(10) == 500.0
    assert p(20) == 500.0

def test_spike_profile():
    p = spike_profile(base_rps=100.0, spike_multiplier=3.0, spike_start=10, spike_duration=5)
    assert p(5) == 100.0
    assert p(10) == 300.0
    assert p(14) == 300.0
    assert p(15) == 100.0

def test_diurnal_profile():
    p = diurnal_profile(base_rps=200.0, amplitude=50.0, period_ticks=100)
    assert p(0) == pytest.approx(200.0)
    assert p(25) == pytest.approx(250.0)  # sin(pi/2) = 1
    assert p(50) == pytest.approx(200.0)  # sin(pi) = 0
    assert p(75) == pytest.approx(150.0)  # sin(3pi/2) = -1

def test_soak_profile():
    p = soak_profile(constant_rps=250.0)
    assert p(0) == 250.0
    assert p(100) == 250.0
