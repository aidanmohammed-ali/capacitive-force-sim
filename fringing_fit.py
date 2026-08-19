"""
@file fringing_fit.py
@author Aidan Mohammed-Ali
@brief Offline fringing capacitance extraction and curve fitting.
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
import analytical as AN
import mom

def extract_fringing_constant(N: int = 10, F_max: float = 5.0, steps: int = 50):
    """
    @brief Sweeps force to extract the quadratic fringing coefficients.
    @param N The number of grid elements per side (N x N grid) for the MoM solver.
    @param F_max The maximum applied force in Newtons (N).
    @param steps The number of data points to generate for the regression.
    @return A tuple containing the coefficients (alpha, beta, gamma).
    """
    # Create an array of force values to test
    forces = np.linspace(0, F_max, steps)
    c_fringe = np.zeros(steps)
    
    print(f"Generating MoM dataset across {steps} force steps...")
    print(f"Using a grid resolution of N={N} ({N*N} total patches)...")
    
    for i, force in enumerate(forces):
        # Calculate theoretical parallel-plate capacitance
        c_ideal = AN.calculate_analytical_capacitance(force)
        
        # Calculate highly accurate MoM capacitance (using default N=10)
        c_mom = mom.calculate_mom_capacitance(N=N, force=force)
        
        # Isolate purely the fringing fields
        c_fringe[i] = c_mom - c_ideal
    
    # Fit a 2nd-degree polynomial: alpha*F^2 + beta*F + gamma
    coeffs = np.polyfit(forces, c_fringe, 2)
    alpha, beta, gamma = coeffs
    
    print("\n=== Fringing Curve-Fit Results ===")
    print(f"Alpha (F^2) : {alpha:e}")
    print(f"Beta  (F^1) : {beta:e}")
    print(f"Gamma (F^0) : {gamma:e}")
    
    return alpha, beta, gamma

if __name__ == "__main__":
    # Run extraction if this script is executed directly
    extract_fringing_constant(N=20, F_max=5.0, steps=50)
