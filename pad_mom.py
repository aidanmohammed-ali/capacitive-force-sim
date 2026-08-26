"""
@file pad_mom.py
@author Aidan Mohammed-Ali
@brief Method of Moments (MoM) solver for rectangular ZIF connector pad capacitance.
@date 2026-08-26
"""

# =============================
# Frameworks
# =============================
import numpy as np

# =============================
# Custom Modules
# =============================
import config as CF

def calculate_pad_mom_capacitance(N: int = 10, voltage: float = 1.0) -> float:
    """
    @brief Calculate ZIF connector pad capacitance including fringing using MoM.
    @param N Number of grid elements along the pad width (determines square patch size).
    @param voltage Applied electrical potential in Volts (V).
    @return Total static pad capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Pad dimension and dielectric thickness
    w = conf.pad_w
    L = conf.pad_L
    d = conf.d_flex
    
    # Geometry and meshing
    patch_L = w / N
    Ny = int(np.round(L / patch_L))
    num_patches = N * Ny
    
    # Permittivity of air
    eps = conf.EPSILON_0 * conf.eps_r_flex
    
    # Coordinate grid for patch centres
    coords = np.zeros((num_patches, 2))
    idx = 0
    for i in range(N):
        for j in range(Ny):
            coords[idx] = [i * patch_L + (patch_L / 2.0), j * patch_L + (patch_L / 2.0)]
            idx += 1
    
    # Assemble P-matrix
    P = np.zeros((num_patches, num_patches))
    coef = 1.0 / (4.0 * np.pi * eps)
    
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
    
    # Solve for charge vector in air gap
    V = np.ones(num_patches) * voltage
    Q = np.linalg.solve(P, V)
    
    # Air gap capacitance
    c_total = float(np.sum(Q) / voltage)
    
    return float(c_total)
