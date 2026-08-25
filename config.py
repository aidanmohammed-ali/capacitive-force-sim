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
    d_air_0: float
    d_flex: float
    gap: float
    
    # Trace Routing & Hardware Limits
    tail_w: float
    tail_L: float
    tail_h: float
    dimple_edge: float
    dimple_corner: float
    cdc_limit: float
    cdc_offset: float
    pad_w: float
    pad_L: float
    
    # Material
    E: float
    nu: float
    eps_r_flex: float
    
    # Derived Properties
    A0: float
    C_flex: float
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
    d_air_0 = parser.getfloat('Geometry', 'd_air_0')
    d_flex = parser.getfloat('Geometry', 'd_flex')
    gap = parser.getfloat('Geometry', 'gap')
    
    # Parse Trace Routing & Hardware Limits
    tail_w = parser.getfloat('Hardware', 'tail_w')
    tail_L = parser.getfloat('Hardware', 'tail_L')
    tail_h = parser.getfloat('Hardware', 'tail_h')
    dimple_edge = parser.getfloat('Hardware', 'dimple_edge')
    dimple_corner = parser.getfloat('Hardware', 'dimple_corner')
    cdc_limit = parser.getfloat('Hardware', 'cdc_limit')
    cdc_offset = parser.getfloat('Hardware', 'cdc_offset')
    pad_w = parser.getfloat('Hardware', 'pad_w')
    pad_L = parser.getfloat('Hardware', 'pad_L')
    
    # Parse Material
    E = parser.getfloat('Material', 'E')
    nu = parser.getfloat('Material', 'nu')
    eps_r_flex = parser.getfloat('Material', 'eps_r_flex')
    
    # Calculate Derived Properties
    A0 = L0 ** 2
    
    C_flex = (eps_0 * eps_r_flex * A0) / d_flex
    
    C_air_initial = (eps_0 * 1.0006 * A0) / d_air_0
    C0 = 1.0 / ((2.0 / C_flex) + (1.0 / C_air_initial))
    
    return SensorConfig(
        EPSILON_0=eps_0,
        L0=L0,
        d_air_0=d_air_0,
        d_flex=d_flex,
        gap=gap,
        tail_w=tail_w,
        tail_L=tail_L,
        tail_h=tail_h,
        dimple_edge=dimple_edge,
        dimple_corner=dimple_corner,
        cdc_limit=cdc_limit,
        cdc_offset=cdc_offset,
        pad_w=pad_w,
        pad_L=pad_L,
        E=E,
        nu=nu,
        eps_r_flex=eps_r_flex,
        A0=A0,
        C_flex=C_flex,
        C0=C0
    )
