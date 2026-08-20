# Capacitive Force Simulator

A Method of Moments (MoM) physics engine and real-time visualiser for characterising capacitive tactile sensors.

## What is this?
This tool mathematically simulates the non-linear fringing fields and spatial crosstalk of a capacitive tactile matrix. It was built to theoretically characterise the hardware limits of physical sensor boards running on chips like Capacitance-to-Digital Converters. 

## Features
* **MoM Extraction:** Computes absolute base capacitance ($C$) and extracts spatial edge/corner crosstalk coefficients.
* **Charge & Voltage Characterisation:** Simulates the physical $1$ V excitation to calculate the exact hardware charge transfer.
* **Real-Time Visualisation:** A Pygame-based GUI to simulate multi-touch forces and physical boundary effects.

## Quick Start
1. Install dependencies:
    `pip install -r requirements.txt`
2. Run the calibration script to generate the physics coefficients:
    `python3 calibrate.py`
3. Launch the interactive GUI:
    `python3 gui_sim.py`
