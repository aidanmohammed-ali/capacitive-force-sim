"""
@file crosstalk_mom.py
@author Aidan Mohammed-Ali
@brief Mutual capacitance Method of Moments (MoM) solver for 3x3 taxel grid.
@date 2026-08-20
"""

# =============================
# Frameworks
# =============================
import numpy as np

# =============================
# Custom Modules
# =============================
import config as CF

def calculate_crosstalk_capacitance(N: int = 4, force: float = 0.0, voltage: float = 1.0) -> dict:
    """
    @brief Calculates self, edge, and corner capacitance in a 3x3 array.
    @param N The number of grid elements per side for a SINGLE taxel.
    @param force The applied normal force in Newtons (N) on the centre taxel.
    @param voltage The electrical potential applied to the active centre taxel in Volts (V).
    @return A dictionary containing 'centre', 'edge', and 'corner' capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Calculate the compressed gap distance d(F)
    delta_d = force / (conf.A0 * conf.E)
    if delta_d >= conf.d_air_0:
        delta_d = conf.d_air_0 * 0.999
    d = conf.d_air_0 - delta_d
    
    # Geometry and Meshing
    patch_L = conf.L0 / N
    patches_per_taxel = N * N
    total_patches = 9 * patches_per_taxel
    pitch = conf.L0 + conf.gap
    eps = conf.EPSILON_0 * 1.0006
    
    # Arrays for the linear system
    coords = np.zeros((total_patches, 2))
    V = np.zeros(total_patches)
    regions = []
    
    idx = 0
    # Loop over the 3x3 grid (Rows and Cols from -1 to 1)
    for row in [-1, 0, 1]:
        for col in [-1, 0, 1]:
            # Determine the taxel's topological region and applied voltage
            if row == 0 and col == 0:
                region = "centre"
                v_applied = voltage
            elif abs(row) == 1 and abs(col) == 1:
                region = "corner"
                v_applied = 0.0
            else:
                region = "edge"
                v_applied = 0.0
            
            # Calculate the physical centre coordinate of this taxel
            taxel_cx = row * pitch
            taxel_cy = col * pitch
            start_x = taxel_cx - (conf.L0 / 2)
            start_y = taxel_cy - (conf.L0 / 2)
            
            # Mesh the individual taxel into N x N patches
            for i in range(N):
                for j in range(N):
                    px = start_x + i * patch_L + (patch_L / 2)
                    py = start_y + j * patch_L + (patch_L / 2)
                    
                    coords[idx] = [px, py]
                    V[idx] = v_applied
                    regions.append(region)
                    idx += 1
    
    # Initialise and populate the P-matrix
    P = np.zeros((total_patches, total_patches))
    coef = 1 / (4 * np.pi * eps)
    
    for i in range(total_patches):
        for j in range(total_patches):
            if i == j:
                term1 = (4 * np.log(1 + np.sqrt(2))) / patch_L
                term2 = 1 / (2 * d)
                P[i, j] = coef * (term1 - term2)
            else:
                R_ij = np.linalg.norm(coords[i] - coords[j])
                image_distance = np.sqrt(R_ij**2 + (2 * d)**2)
                P[i, j] = coef * ((1 / R_ij) - (1 / image_distance))
    
    # Solve for the distance charge vector
    Q = np.linalg.solve(P, V)
    
    # Partition the charge based on the taxel region
    q_centre = 0.0
    q_edge = 0.0
    q_corner = 0.0
    
    for k in range(total_patches):
        if regions[k] == "centre":
            q_centre += Q[k]
        elif regions[k] == "edge":
            q_edge += Q[k]
        elif regions[k] == "corner":
            q_corner += Q[k]
    
    # Return the partitioned capacitance map
    return {
        "centre": float(q_centre),
        "edge": float(q_edge) / 4.0,
        "corner": float(q_corner) / 4.0
    }
