"""
@file test_mom.py
@author Aidan Mohammed-Ali
@brief Unit tests for the MoM capacitance solver.
@date 2026-08-19
"""

# =============================
# Frameworks
# =============================
import pytest

# =============================
# Custom Modules
# =============================
import analytical as AN
import mom

def test_mom_vs_analytical_zero_force():
    """
    @brief Verifies MoM capacitance is slightly higher than analytical due to fringing fields.
    """
    C_analytical = AN.calculate_analytical_capacitance(0.0)
    C_mom = mom.calculate_mom_capacitance(N=4, force=0.0) # Use N=4 for a fast test
    
    # MoM should be strictly greater than the ideal analytical model
    assert C_mom > C_analytical, f"MoM ({C_mom}) should be > Analytical ({C_analytical})"

def test_mom_positive_force():
    """
    @brief Verifies MoM capacitance increases when force is applied.
    """
    C_unloaded = mom.calculate_mom_capacitance(N=4, force=0.0)
    C_loaded = mom.calculate_mom_capacitance(N=4, force=1.0)
    
    assert C_loaded > C_unloaded, "MoM capacitance must increase under load."
