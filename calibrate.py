"""
@file calibrate.py
@author Aidan Mohammed-Ali
@brief Runs all MoM extractions and exports the polynomial coefficients to JSON.
@date 2026-08-20
"""

# =============================
# Frameworks
# =============================
import json

# =============================
# Custom Modules
# =============================
import fringing_fit as FF
import crosstalk_fit as CTF

def generate_calibration_file(filename: str = "constants.json"):
    """
    @brief Extracts fringing and crosstalk constants and saves them to a file.
    @param filename The name of the output JSON file to save the coefficients to.
    """
    print("==================================================")
    print("  STARTING MASTER CALIBRATION (MoM EXTRACTION)    ")
    print("==================================================")
    
    # Run the fringing extraction (N=10 for high accuracy)
    print("\n--- Step 1: Self-Capacitance Fringing ---")
    alpha, beta, gamma = FF.extract_fringing_constants(N=10, F_max=5.0, steps=50)
    
    # Run the mutual crosstalk extraction (N=10 high for accuracy)
    print("\n--- Step 2: Mutual Capacitance Crosstalk ---")
    crosstalk_results = CTF.extract_crosstalk_constants(N=10, F_max=5.0, steps=50)
    
    # Format the data dictionary
    calibration_data = {
        "fringing": {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma
        },
        "crosstalk": {
            "edge": {
                "alpha": crosstalk_results["edge"][0],
                "beta": crosstalk_results["edge"][1],
                "gamma": crosstalk_results["edge"][2]
            },
            "corner": {
                "alpha": crosstalk_results["corner"][0],
                "beta": crosstalk_results["corner"][1],
                "gamma": crosstalk_results["corner"][2]
            }
        }
    }
    
    # Export to JSON
    with open(filename, "w") as f:
        json.dump(calibration_data, f, indent=4)
    
    print(f"\n[SUCCESS] Calibration complete! Constants saved to {filename}")

if __name__ == "__main__":
    generate_calibration_file()
