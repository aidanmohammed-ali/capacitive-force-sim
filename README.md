# Capacitive Force Simulator

An electrostatic Method of Moments (MoM) physics engine and real-time visualization tool for modeling, calibrating, and testing capacitive tactile sensor matrices.

## Overview
Designing capacitive tactile arrays involves managing complex parasitic capacitance, fringing fields, and spatial crosstalk. This simulator bridges the gap between theoretical electrostatics and real-world hardware design.

It uses a **Method of Moments (MoM)** solver with image-charge theory to pre-calculate physics coefficients, which are then fed into a real-time superposition engine to emulate real hardware operations.

## Key Features
* **Rigorous Electromagnetics:** Implements analytical patch integrations and MoM sovlers for self-capacitance, ZIF pads, and coplanar flex traces.
* **Spatial Crosstalk Modeling:** Simulates mechanical force-spreading and electrical edge/corner coupling between taxels.
* **Interactive Diagnostic GUI:** A real-time Pygame visualiser featuring three distinct operational views:
    * **RAW Mode:** Visualise absolute capacitance (pF) to check hardware limits and CDC saturation.
    * **DELTA Mode:** Emulates firmware baseline subtraction to isolate pure touch signals (fF).
    * **FORCE Mode:** Displays the raw physical mechanical input (N) across the grid.

## Quick Start
1. Install dependencies:
    `pip install -r requirements.txt`
2. Run the calibration script to generate the physics coefficients:
    `python3 calibrate.py`
3. Launch the interactive GUI:
    `python3 gui_sim.py`

## Configuration
All physical dimensions, material properties (Young's Modulus, relative permittivity), and hardware limits can be tuned directly in `config.ini`.

## Documentation
For a deep dive into the underlying mathematics check out the `docs/mathematical_model.md`.
