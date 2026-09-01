# Capacitive Sensor Physics Model
This document outlines the core physics engine driving the tactile simulator. The model fuses an anlytical mechanical deflection baseline with a Method of Moments (MoM) solver to capture real-world parasitic limits and fringing fields.

## 1. Mechanical Membrane Deflection
Because the active compressible dielectric is air, the sensor avoids hyperelastic nonlinearities typical of solid elastomers. The structural compression is modeled as a linear elastic deformation driven by the Young's Modulus ($E$) of the sensor's materials. The mechanical deflection ($\Delta d$) of the air gap under an applied normal force ($F$) is calculated as:
$$
    \Delta d(F) = d_{air\_0} \frac{F}{A_0 E}
$$
Where $d_{air\_0}$ is the initial gap and $A_0$ is the nominal taxel area. A hardware limit caps $\Delta d$ to prevent unphysical intersections.

## 2. Ideal Series Capacitance
The ideal baseline assumes an infinite plane, modeled as a series circuit of three distinct dielectric layers: the top flex PCB, the active air gap, and the bottom flex PCB.
$$
    C_{ideal} = \left( \frac{2}{C_{flex}} + \frac{1}{C_{air}} \right)^{-1}
$$

* **Fixed PCB Layers:** $C_{flex} = \frac{\varepsilon_0 \varepsilon_{r\_flex} A_{0}}{d_{flex}}$
* **Dynamic Air Gap:** Utilising a Taylor expansion for computational efficiency, the air gap dynamically scales with mechanical strain:
$$
    C_{air} = C_{0} \left( 1 + \frac{F_{i,j}}{A_{0} E} \right)
$$

## 3. Electromagnetic Fringing & Crosstalk
Ideal parallel-plate mathematics is insufficient for capturing the non-linear realities of physical hardware. To account for this, a Method of Moments (MoM) solver is used to evaluate the 3D charge distribution across the grid.
* **Fringing Fields:** Captures the electric field lines bowing outward at the edges of the tiny $A_{0}$ pads.
* **Trace Parasitics:** Models the static coplanar mutual capacitance of the FR4 PCB microstrips, incorporating infinite ground-plane image theory.
* **Flex Tail Parasitics:** Models the static coplanar mutual capacitance of the flex PCB traces.
* **Spatial Crosstalk:** Evaluates a $3 \times 3$ bounding box to extract electromagnetic coupling to adjacent edge and corner taxels.

To run at real-time speeds, the complex MoM physics are executed offline and curve-fitted into a lightweight polynomial transfer function that is superimposed over the active grid:
$$
    C_{total}(F_{i,j}) = C_{ideal} + (\alpha F_{i,j}^2 + \beta F_{i,j} + \gamma)
$$

## 4. Global Matrix Superposition
During active matrix scanning, the raw measured capacitance $C_{meas}(i,j)$ under multi-taxel loading is the sum of its local deformation and the spatial crosstalk from surrounding active nodes.
The inter-taxel mutual coupling datasets are curve-fitted into low-order polynomials ($C_{edge}$ and $C_{corner}$) based on the physical gap between adjacent taxels. The final measured readout is calculated via superposition:
$$
    C_{meas}(i,j) \approx C_{total}(F_{i,j}) + \sum_{(u,v) \in Edge} C_{edge}(F_{i+u, j+v}) + \sum_{(u,v) \in Corner} C_{corner}(F_{i+u, j+v})
$$
