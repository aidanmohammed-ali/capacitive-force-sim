"""
@file mom.py
@author Aidan Mohammed-Ali
@brief Method of Moments (MoM) capacitance solver.
@date 2026-08-19
"""

# =============================
# Frameworks
# =============================
import numpy as np

# =============================
# Custom Modules
# =============================
import config as CF

def calculate_mom_capacitance(N: int = 10, force: float = 0.0, voltage: float = 1.0) -> float:
    """
    @brief Calculate capacitance using MoM with image theory.
    @param N The number of grid elements per side (N x N grid).
    @param force The applied normal force in Newtons.
    @param voltage The electrical potential applied to the top plate in Volts (V).
    @return The calculated capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Calculate the compressed gap distance d(F)
    delta_d = force / (conf.A0 * conf.E)
    if delta_d >= conf.d_air_0:
        delta_d = conf.d_air_0 * 0.999
    d = conf.d_air_0 - delta_d
            
    # Discretisation geometry
    num_patches = N * N
    patch_L = conf.L0 / N
    patch_A = patch_L ** 2
    
    # Permittivity of the air gap
    eps = conf.EPSILON_0 * 1.0006
    
    # Initialise the P-matrix
    P = np.zeros((num_patches, num_patches))
    
    # Create coordinate grid for the patches
    coords = np.zeros((num_patches, 2))
    idx = 0
    for i in range(N):
        for j in range(N):
            coords[idx] = [i * patch_L + (patch_L / 2), j * patch_L + (patch_L / 2)]
            idx += 1
    
    # Pre-calculate the permittivity coefficient
    coef = 1 / (4 * np.pi * eps)
    
    # Populate the P-matrix
    for i in range(num_patches):
        for j in range(num_patches):
            if i == j:
                # Diagonal Elements: Self-potential minus direct image charge
                term1 = (4 * np.log(1 + np.sqrt(2))) / patch_L
                term2 = 1 / (2 * d)
                P[i, j] = coef * (term1 - term2)
            else:
                # Off-Diagonal: Mutual-potential minus mutual image charge
                R_ij = np.linalg.norm(coords[i] - coords[j])
                image_distance = np.sqrt(R_ij**2 + (2 * d)**2)
                P[i, j] = coef * ((1 / R_ij) - (1 / image_distance))
    
    # Define the voltage vector (assume 1 Volt applied to top plate)
    V = np.ones(num_patches) * voltage
    
    # Solve for discrete charge vector: [q] = [P]^-1 [V]
    Q = np.linalg.solve(P, V)
    
    # Total Capacitance C = Q_total / V_applied
    C_total = np.sum(Q) / voltage
    
    return float(C_total)
