"""
@file crosstalk_fit.py
@author Aidan Mohammed-Ali
@brief Offline crosstalk capacitance extraction and curve fitting.
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
import crosstalk_mom as CTM

def extract_crosstalk_constants(N: int = 3, F_max: float = 5.0, steps: int = 50):
    """
    @brief Sweeps force to extract quadratic coefficients for edge and corner crosstalk.
    @param N The number of grid elements per side for a SINGLE taxel.
    @param F_max The maximum applied force in Newtons (N).
    @param steps The number of data points to generate for the regression.
    @return A dictionary containing the fitted coefficients for 'edge' and 'corner'.
    """
    forces = np.linspace(0, F_max, steps)
    c_edge_data = np.zeros(steps)
    c_corner_data = np.zeros(steps)
    
    print(f"Generating 3x3 MoM crosstalk dataset across {steps} force steps...")
    print(f"Using a grid resolution of N={N} per taxel (total {9 * N * N} patches)...")
    print("This requires large matrix inversions and will take some time...")
    
    for i, force in enumerate(forces):
        # Calculate the mutual capacitance map at this specific force
        results = CTM.calculate_crosstalk_capacitance(N=N, force=force)
        
        # Store the raw mutual capacitance values
        c_edge_data[i] = results["edge"]
        c_corner_data[i] = results["corner"]
    
    # Fit 2nd-degree polynomials: alpha*F^2 + beta*F + gamma
    edge_coeffs = np.polyfit(forces, c_edge_data, 2)
    corner_coeffs = np.polyfit(forces, c_corner_data, 2)
    
    alpha_e, beta_e, gamma_e = edge_coeffs
    alpha_c, beta_c, gamma_c = corner_coeffs
    
    print("\n=== Edge Crosstalk Curve-Fit Results ===")
    print(f"Alpha_e (F^2) : {alpha_e:e}")
    print(f"Beta_e  (F^1) : {beta_e:e}")
    print(f"Gamma_e (F^0) : {gamma_e:e}")
    
    print("\n=== Corner Crosstalk Curve-Fit Results ===")
    print(f"Alpha_c (F^2) : {alpha_c:e}")
    print(f"Beta_c  (F^1) : {beta_c:e}")
    print(f"Gamma_c (F^0) : {gamma_c:e}")
    
    return {
        "edge": (alpha_e, beta_e, gamma_e),
        "corner": (alpha_c, beta_c, gamma_c)
    }

if __name__ == "__main__":
    # N=3 is used for speed, but N=4 or N=5 will provide better mesh convergence
    extract_crosstalk_constants(N=3, F_max=5.0, steps=50)
