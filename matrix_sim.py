"""
@file matrix_sim.py
@author Aidan Mohammed-Ali
@brief Full matrix superposition simulator using extracted MoM coefficients.
@date 2026-08-20
"""

# =============================
# Frameworks
# =============================
import json
import numpy as np

# =============================
# Custom Modules
# =============================
import config as CF
import analytical as AN

def load_calibration(filename: str = "constants.json") -> dict:
    """
    @brief Loads the pre-calculated MoM coefficients from JSON.
    """
    with open(filename, "r") as f:
        return json.load(f)

def simulate_matrix_readout(force_grid: np.ndarray, cal_data: dict) -> np.ndarray:
    """
    @brief Simulates the final capacitance readout of a full 2D sensor matrix.
    @param force_grid A 2D numpy array representing the force applied to each taxel in Newtons (N).
    @param cal_data Dictionary containing all fringing and crosstalk coefficients.
    @return A 2D numpy array of the total measured capacitance at each node in Farads (F).
    """
    rows, cols = force_grid.shape
    ideal_matrix = np.zeros((rows, cols))
    readout_matrix = np.zeros((rows, cols))
    
    conf = CF.load_config("config.ini")
    
    # Mechanical Flex Coupling
    effective_force = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            F_applied = force_grid[r, c]
            if F_applied > 0:
                effective_force[r, c] += F_applied
                
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if 0 <= r + dr < rows and 0 <= c + dc < cols:
                        effective_force[r + dr, c + dc] += F_applied * conf.dimple_edge
                
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if 0 <= r + dr < rows and 0 <= c + dc < cols:
                        effective_force[r + dr, c + dc] += F_applied * conf.dimple_corner
    
    # Hardware Parasitics
    c_pad = cal_data["pad"]["c_pad"]
    c_trace_self = cal_data["trace"]["c_trace_self"]
    c_trace_mutual = cal_data["trace"]["c_trace_mutual"]
    c_pcb_self = cal_data["pcb"]["c_pcb_self"]
    c_pcb_mutual = cal_data["pcb"]["c_pcb_mutual"]
        
    # Unpack coefficients
    alpha = cal_data["fringing"]["alpha"]
    beta = cal_data["fringing"]["beta"]
    gamma = cal_data["fringing"]["gamma"]
    
    edge = cal_data["crosstalk"]["edge"]
    corner = cal_data["crosstalk"]["corner"]
    
    # Calculate Ideal Physical States
    for r in range(rows):
        for c in range(cols):
            F = effective_force[r, c]
            
            # Base Capacitance (Flex-Air-Flex)
            c_ideal = AN.calculate_analytical_capacitance(F)
            c_fringe = (alpha * F**2) + (beta * F) + gamma
            c_node = c_ideal + c_fringe
            
            # Crosstalk Superposition
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if 0 <= r + dr < rows and 0 <= c + dc < cols:
                    F_neigh = force_grid[r + dr, c + dc]
                    c_node += (edge["alpha"] * F_neigh**2) + (edge["beta"] * F_neigh) + edge["gamma"]
            
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                if 0 <= r + dr < rows and 0 <= c + dc < cols:
                    F_neigh = force_grid[r + dr, c + dc]
                    c_node += (corner["alpha"] * F_neigh**2) + (corner["beta"] * F_neigh) + corner["gamma"]
            
            ideal_matrix[r, c] = c_node
    
    # Emulate CDC Hardware
    for r in range(rows):
        for c in range(cols):
            # Flex tail and PCB traces
            if (c == 0 or c == cols - 1):
                num_neighbours = 1
            else:
                num_neighbours = 2
            c_flex_tail = (num_neighbours * c_trace_mutual) + c_trace_self
            c_pcb = (num_neighbours * c_pcb_mutual) + c_pcb_self
            
            # Total static parasitic baseline
            c_parasitics_total = conf.cdc_offset + c_pad + c_flex_tail + c_pcb
            
            # Final matrix
            readout_matrix[r, c] = ideal_matrix[r, c] + c_parasitics_total
    
    return readout_matrix

if __name__ == "__main__":
    cal_data = load_calibration("constants.json")
    
    # Capture the unloaded baseline matrix
    baseline_forces = np.zeros((5, 5))
    baseline_matrix = simulate_matrix_readout(baseline_forces, cal_data)
    
    # Apply a 2.0 N force to the dead centre
    active_forces = np.zeros((5, 5))
    active_forces[2, 2] = 2.0
    
    # Read the raw active matrix and subtract the baseline
    raw_matrix = simulate_matrix_readout(active_forces, cal_data)
    delta_matrix = raw_matrix - baseline_matrix
    
    print("=== Raw CDC Measurement (Absolute Farads) ===")
    with np.printoptions(precision=3, suppress=False):
        print(raw_matrix)

    print("\n=== Firmware Signal (Delta Farads) ===")
    with np.printoptions(precision=3, suppress=False):
        print(delta_matrix)
