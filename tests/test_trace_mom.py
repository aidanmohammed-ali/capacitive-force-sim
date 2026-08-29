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
    c_self, c_mutual = trace_mom.calculate_coplanar_trace_capacitance(Nw=2, Nl=40, voltage=1.0)
    
    # MoM must be strictly greater than sidewall parallel-plate model
    assert c_mutual > c_sidewall, (
        f"MoM mutual capacitance ({c_mutual:.4e} F) should be significantly greater than "
        f"the sidewall model ({c_sidewall:.4e} F)"
    )

def test_trace_mom_positivity():
    """
    @brief Verifies the extracted self and mutual capacitances are strictly positive.
    """
    c_self, c_mutual = trace_mom.calculate_coplanar_trace_capacitance(Nw=2, Nl=40, voltage=1.0)
    
    assert c_self > 0.0, f"Self capacitance must be strictly positive, got {c_self}"
    assert c_mutual > 0.0, f"Mutual capacitance must be strictly positive, got {c_mutual}"
