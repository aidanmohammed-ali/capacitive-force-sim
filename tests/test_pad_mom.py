"""
@file test_pad_mom.py
@author Aidan Mohammed-Ali
@brief Unit tests for the ZIF connector pad MoM capacitance solver.
@date 2026-08-26
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
import pad_mom

def test_mom_vs_analytical_zero_force():
    """
    @brief Verifies pad MoM capacitance is slightly higher than the ideal parallel-plate series model due to fringing fields.
    """
    conf = CF.load_config("config.ini")
    
    # Ideal parallel-plate series capacitance equivalent
    w = conf.pad_w
    L = conf.pad_L
    d = conf.d_flex
    
    c_pad_analytical = (conf.EPSILON_0 * conf.eps_r_flex * w * L) / d
    
    # MoM calculation
    c_pad_mom = pad_mom.calculate_pad_mom_capacitance(N=4, voltage=1.0) # Use N=4 for a fast test
    
    # MoM should be strictly greater than the ideal analytical model
    assert c_pad_mom > c_pad_analytical, f"MoM ({c_pad_mom}) should be > Analytical ({c_pad_analytical})"

