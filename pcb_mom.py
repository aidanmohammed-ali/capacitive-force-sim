"""
@file pcb_mom.py
@author Aidan Mohammed-Ali
@brief Method of Moments (MoM) solver for pcb trace self capacitance and coplanar trace-to-trace mutual capacitance.
@date 2026-08-29
"""

# =============================
# Frameworks
# =============================
import numpy as np

# =============================
# Custom Modules
# =============================
import config as CF

def calculate_pcb_capacitance(Nw: int = 2, Nl: int = 40, voltage: float = 1.0) -> float:
    """
    @brief Computes self capacitance and mutual coupling between two parallel coplanar traces on the pcb using MoM.
    @param Nw Number of discrete segments across the trace width.
    @param Nl Number of discrete segments across the trace length.
    @param voltage Applied test potential on the active trace in Volts (V).
    @return Trace self capacitance in Farads (F).
            Trace-to-trace mutual capacitance in Farads (F).
    """
    conf = CF.load_config("config.ini")
    
    # Trace geometry
    w = conf.pcb_w
    s = conf.pcb_s
    L = conf.pcb_L
    
    # PCB permittivity
    eps_eff = conf.EPSILON_0 * ((conf.eps_r_fr4 + 1.0) / 2.0)
    
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
    coef = 1.0 / (4.0 * np.pi * eps_eff)
    
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
                P[i, j] = coef * (diag_geom - (1 / (2 * conf.d_pcb)))
            else:
                # Off-Diagonal: Coulomb interaction between distinct patch centres
                R_ij = np.linalg.norm(coords[i] - coords[j])
                image_distance = np.sqrt(R_ij**2 + (2 * conf.d_pcb)**2)
                P[i, j] = coef * ((1.0 / R_ij) - (1.0 / image_distance))
    
    # Solve for surface charge vector
    Q = np.linalg.solve(P, V)
    
    # Extract total charge on trace 1
    q_trace1 = np.sum(Q[:patches_per_trace])
    c_total = float(q_trace1 / voltage)
    
    # Extract induced mutual charge on trace 2
    q_trace2 = np.abs(np.sum(Q[patches_per_trace:]))
    c_mutual = float(q_trace2 / voltage)
    
    # Self capacitance to ground
    c_self = c_total - c_mutual
    
    return c_self, c_mutual
