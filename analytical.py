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
    
    # Mechanical Deflection
    delta_d = force / (conf.A0 * conf.E)
    
    # Hard Limit
    if delta_d >= conf.d_air_0:
        delta_d = conf.d_air_0 * 0.999
    
    current_air_gap = conf.d_air_0 - delta_d
    
    # Electrical Series Model
    C_air = (conf.EPSILON_0 * 1.0 * conf.A0) / current_air_gap
    C_total = 1.0 / ((2.0 / conf.C_flex) + (1.0 / C_air))
    
    return C_total
