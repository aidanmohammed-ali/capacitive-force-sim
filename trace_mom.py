"""
@file trace_mom.py
@author Aidan Mohammed-Ali
@brief Method of Moments (MoM) solver for coplanar trace-to-trace mutual capacitance.
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

def calculate_coplanar_trace_capacitance(Nw: int = 2, Nl: int = 40, voltage: float = 1.0) -> float:
    """
    @brief Computes mutual coupling between two parallel coplanar traces on the flexible tail using MoM.
    @param Nw Number of discrete segments across the trace width.
    @param Nl Number of discrete segments across the trace length.
    @param voltage Applied test potential on the active trace in Volts (V).
    @return Trace-to-trace mutual capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Trace geometry
    w = conf.flex_trace_w
    s = conf.flex_trace_s
    L = conf.flex_trace_L
    
    # Flex permittivity
    eps = conf.EPSILON_0 * conf.eps_r_flex
    
    # Geometry and meshing
    dx = w / Nw
    dy = L / Nl
    patches_per_trace = Nw * Nl
    total_patches = 2 * patches_per_trace
    
    coords = np.zeros((total_patches, 2))
    V = np.zeros(total_patches)
    
    # Trace 1: Active Driver
    idx = 0
    for i in range(Nw):
        for j in range(Nl):
            px = i * dx + (dx / 2.0)
            py = j * dy + (dy / 2.0)
            coords[idx] = [px, py]
            V[idx] = voltage
            idx += 1
    
    # Trace 2: Sensing Line
    for i in range(Nw):
        for j in range(Nl):
            px = (w + s) + i * dx + (dx / 2.0)
            py = j * dy + (dy / 2.0)
            coords[idx] = [px, py]
            V[idx] = 0.0
            idx += 1
    
    # Assemble P-matrix
    P = np.zeros((total_patches, total_patches))
    coef = 1.0 / (4.0 * np.pi * eps)
    
    # Exact analytical self-potential integral for a rectangular patch
    diag_geom = (2.0 / (dx * dy)) * (
        dx * np.arcsinh(dy / dx) +
        dy * np.arcsinh(dx / dy)
    )
    
    # Assemble P-matrix
    for i in range(total_patches):
        for j in range(total_patches):
            if i == j:
                # Diagonal: Self-potential integral over surface panel
                P[i, j] = coef * diag_geom
            else:
                # Off-Diagonal: Coulomb interaction between distinct patch centres
                R_ij = np.linalg.norm(coords[i] - coords[j])
                P[i, j] = coef * (1.0 / R_ij)
    
    # Solve for surface charge vector
    Q = np.linalg.solve(P, V)
    
    # Extract induced mutual charge on trace 2
    q_trace2 = np.abs(np.sum(Q[patches_per_trace:]))
    c_mutual = float(q_trace2 / voltage)
    
    return c_mutual
