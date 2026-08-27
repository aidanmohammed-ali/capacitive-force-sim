"""
@file test_trace_mom.py
@author Aidan Mohammed-Ali
@brief Unit tests for the flex coplanar trace-to-trace MoM capacitance solver.
@date 2026-08-27
"""

# =============================
# Frameworks
# =============================
import pytest

# =============================
# Custom Modules
# =============================
import config as CF
import trace_mom

def test_trace_mom_vs_sidewall():
    """
    @brief Verifies coplanar MoM capacitance is slightly higher than the sidewall parallel-plate series model due to fringing fields.
    """
    conf = CF.load_config("config.ini")
    
    # Parallel-plate capacitance
    t = 1.8e-5
    s = conf.flex_trace_s
    L = conf.flex_trace_L
    eps = conf.EPSILON_0 * conf.eps_r_flex
    
    c_sidewall = (eps * t * L) / s
    
    # MoM calculation
    c_coplanar_mom = trace_mom.calculate_coplanar_trace_capacitance(Nw=2, Nl=40, voltage=1.0)
    
    # MoM must be strictly greater than sidewall parallel-plate model
    assert c_coplanar_mom > c_sidewall, (
        f"MoM ({c_coplanar_mom:.4e} F) should be significantly greater than "
        f"the sidewall model ({c_sidewall:.4e} F)"
    )

def test_trace_mom_positivity():
    """
    @brief Verifies the extracted capacitance is strictly positive.
    """
    c_val = trace_mom.calculate_coplanar_trace_capacitance(Nw=2, Nl=40, voltage=1.0)
    
    assert c_val > 0.0, "Capacitance must be strictly positive."
