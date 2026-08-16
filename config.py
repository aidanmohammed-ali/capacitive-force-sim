"""
@file config.py
@author Aidan Mohammed-Ali
@brief Configuration parser and data structures for the tactile capacitive sensor simulation.
@date 2026-08-16
"""

# =============================
# Frameworks
# =============================
import configparser
import dataclasses as dc

"""
@brief Data class representing the physical, geometric, and material properties of the sensor.
"""
@dc.dataclass
class SensorConfig:
    # Constants
    EPSILON_0: float
    
    # Geometry
    L0: float
    d0: float
    gap: float
    
    # Material
    E: float
    nu: float
    eps_r: float
    
    # Derived Properties
    A0: float
    C0: float

def load_config(ini_file: str = "config.ini") -> SensorConfig:
    """
    @brief Parse the INI configuration file, calculate derived values, and returns a configuration object.
    @param ini_file The path to the configuration file (default: "config.ini").
    @return SensorConfig Populated dataclass containing all sensor parameters.
    @raise FileNotFoundError If the specified INI file cannot be found or read.
    """
    parser = configparser.ConfigParser()
    
    # Read the file and check if it actually loaded
    if not parser.read(ini_file):
        raise FileNotFoundError(f"Could not find or open '{ini_file}'")
    
    # Parse Constants
    eps_0 = parser.getfloat('Constants', 'EPSILON_0')
    
    # Parse Geometry
    L0 = parser.getfloat('Geometry', 'L0')
    d0 = parser.getfloat('Geometry', 'd0')
    gap = parser.getfloat('Geometry', 'gap')
    
    # Parse Material
    E = parser.getfloat('Material', 'E')
    nu = parser.getfloat('Material', 'nu')
    eps_r = parser.getfloat('Material', 'eps_r')
    
    # Calculate Derived Properties
    A0 = L0 ** 2
    C0 = (eps_0 * eps_r * A0) / d0
    
    return SensorConfig(
        EPSILON_0=eps_0,
        L0=L0,
        d0=d0,
        gap=gap,
        E=E,
        nu=nu,
        eps_r=eps_r,
        A0=A0,
        C0=C0
    )
