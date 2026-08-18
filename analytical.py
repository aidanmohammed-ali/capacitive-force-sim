"""
@file analytical.py
@author Aidan Mohammed-Ali
@brief Analytical physics model for the tactile sensor.
@date 2026-08-18 
"""

# =============================
# Custom Modules
# =============================
import config as CF

def calculate_analytical_capacitance(force: float) -> float:
    """
    @brief Calculate the theoretical capacitance under a given applied force.
    @details Uses the linearised parallel-plate model. Automatically accounts for
             electrode rigidity and material stiffness defined in config.ini.
    @param force The applied normal force in Newtons (N).
    @return The calculated capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Calculate the change in capacitance based on the physical model
    expansion_factor = 1 + (2 * conf.nu)
    mechanical_strain = force / (conf.A0 * conf.E)
    
    # Final theoretical capacitance
    C_f = conf.C0 * (1 + (expansion_factor * mechanical_strain))
    
    return C_f
