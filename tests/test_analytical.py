"""
@file test_analytical.py
@author Aidan Mohammed-Ali
@brief Unit tests for the analytical physics model.
@date 2026-08-18
"""

# =============================
# Frameworks
# =============================
import pytest

# =============================
# Custom Modules
# =============================
import config as CF
import analytical as AN

def test_zero_force():
    """
    @brief Verifies that applying 0 Newton force returns the baseline capacitance C0.
    """
    conf = CF.load_config("config.ini")
    force = 0.0
    
    # Calculate using the analytical module
    C_calc = AN.calculate_analytical_capacitance(force)
    
    # At 0 force, capacitance should exactly equal the baseline C0
    assert C_calc == pytest.approx(conf.C0), f"Expected {conf.C0}, got {C_calc}"

def test_positive_force():
    """
    @brief Verifies the capacitance calculation for a 1 Newton applied force.
    """
    conf = CF.load_config("config.ini")
    force = 1.0
    
    # Manual calculation to verify the function's internal logic
    expected_strain = force / (conf.A0 * conf.E)
    expected_C = conf.C0 * (1.0 + expected_strain) # (1 + 2*nu) becomes 1 because nu = 0
    
    C_calc = AN.calculate_analytical_capacitance(force)
    
    # Check if the math matches
    assert C_calc == pytest.approx(expected_C), "Capacitance under load calculated incorrectly"
    
    # Physics sanity check: Pushing down MUST increase capacitance
    assert C_calc > conf.C0, "Capacitance must increase when the sensor is compressed"
