"""
@file test_crosstalk_mom.py
@author Aidan Mohammed-Ali
@brief Unit tests for the mutual capacitance solver.
@date 2026-08-20
"""

# =============================
# Frameworks
# =============================
import pytest

# =============================
# Custom Modules
# =============================
import crosstalk_mom as CTM

def test_crosstalk_decay():
    """
    @brief Verifies that capacitance decays as distance from the active centre increases.
    """
    # Using N=3 for a faster matrix inversion during testing
    results = CTM.calculate_crosstalk_capacitance(N=3, force=0.0)
    
    c_centre = results["centre"]
    c_edge = results["edge"]
    c_corner = results["corner"]
    
    # Physics check: Field strength decays over distance
    assert abs(c_centre) > abs(c_edge), f"Centre ({abs(c_centre):e}) should be > Edge ({abs(c_edge):e})"
    assert abs(c_edge) > abs(c_corner), f"Edge ({abs(c_edge):e}) should be > Corner ({abs(c_corner):e})"

def test_crosstalk_force_response():
    """
    @brief Verifies that applying force increases capacitance across the array.
    """
    unloaded = CTM.calculate_crosstalk_capacitance(N=3, force=0.0)
    loaded = CTM.calculate_crosstalk_capacitance(N=3, force=1.0)
    
    # The centre node directly under the load must increase
    assert loaded["centre"] > unloaded["centre"], "Loaded centre must be greater than unloaded centre"
