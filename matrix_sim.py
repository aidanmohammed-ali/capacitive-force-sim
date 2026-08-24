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
    
    # Unpack coefficients
    alpha = cal_data["fringing"]["alpha"]
    beta = cal_data["fringing"]["beta"]
    gamma = cal_data["fringing"]["gamma"]
    
    edge = cal_data["crosstalk"]["edge"]
    corner = cal_data["crosstalk"]["corner"]
    
    # Calculate Ideal Physical States
    for r in range(rows):
        for c in range(cols):
            F = force_grid[r, c]
            
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
    
    # Calculate static routing tail capacitance
    c_tail_rx = (conf.EPSILON_0 * conf.eps_r_flex * conf.tail_w * conf.tail_L) / conf.tail_h
    
    # Emulate CDC Hardware
    for r in range(rows):
        for c in range(cols):
            # Sum the ideal column slice
            c_pin_rx = c_tail_rx + np.sum(ideal_matrix[:, c])
            
            # Hardware limit check
            if c_pin_rx > conf.cdc_limit:
                readout_matrix[r, c] = np.nan
            else:
                readout_matrix[r, c] = ideal_matrix[r, c]
    
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
