"""
@file test_config.py
@author Aidan Mohammed-Ali
@brief Unit tests for the configuration parser.
@date 2026-08-16
"""

# =============================
# Frameworks
# =============================
import pytest

# =============================
# Custom Modules
# =============================
import config as CF

def test_config_loading():
    """
    @brief Verifies that the configuration parser correctly calculates derived properties (A0, C0) and enforces physical constraints.
    """
    config = CF.load_config("config.ini")
    
    # Verify the derived area A0
    expected_A0 = config.L0 ** 2
    assert config.A0 == expected_A0, f"Area A0 should be {expected_A0}, got {config.A0}"
    
    # Verify the baseline capacitance C0
    expected_C0 = (config.EPSILON_0 * config.eps_r * expected_A0) / config.d0
    assert config.C0 == expected_C0, f"Baseline C0 should {expected_C0}, got {config.C0}"
    
    # Check for physical realities
    assert config.C0 > 0, "Capacitance must be strictly positive."
    assert config.nu == 0, "Poisson's ratio must be 0 for rigid flex PCB traces."
    assert config.eps_r > 0.99, "Relative permittivity for air should be ~1.0"

def test_missing_file():
    """
    @brief Ensures that the configuration parser raises a FileNotFoundError when provided with an invalid path.
    """
    with pytest.raises(FileNotFoundError):
        CF.load_config("does_not_exist.ini")
