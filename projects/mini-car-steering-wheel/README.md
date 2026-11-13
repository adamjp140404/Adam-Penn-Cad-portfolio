# Mini Car Steering Wheel Replacement

![Steering wheel, tapered hub version](renders/Wheel_tpu_Tapered.png)

**Software:** SolidWorks · **Manufacturing:** FDM 3D printing (PETG, PLA, TPU) · **Parts:** 3 (wheel, TPU sleeve, logo insert)

## Overview
A 3D-printed replacement steering wheel for a mini car. It has a three-spoke wheel, a ribbed **TPU sleeve** that friction-fits the wheel onto the steering shaft, and a **logo insert** in the center of the hub.

## Design
| Feature | Dimension |
|---|---|
| Wheel outer diameter | 190.5 mm (7.50 in) |
| Overall depth (rim + hub boss) | 76.2 mm (3.00 in) |
| Rim thickness | 25.4 mm (1.00 in) |
| Hub bore | Ø39.4 mm (1.55 in), lead-in at the opening |
| TPU sleeve | Ø36.8 mm ID × Ø39.4 mm OD × 50.8 mm long, 8 axial ribs to Ø41.9 mm |

**Friction fit:** the sleeve's body matches the hub bore exactly, and its 8 axial ribs stand 1.27 mm proud of it. Pressing the sleeve into the bore squeezes the flexible TPU ribs. That keeps the wheel tight on the shaft without fasteners and absorbs printing tolerances, which are hard to control in a rigid-to-rigid press fit.

## Iterations
| Rev | Part | Change | Files |
|---|---|---|---|
| A | Wheel | Straight cylindrical hub boss, Ø63.5 mm | STL |
| B | Wheel | Tapered transition from hub boss to spokes (boss Ø65.3 mm). The taper made the wheel easier to print and cut down on support material | SLDPRT, STL |
| A | TPU sleeve | 1.27 mm wall, 8 ribs | STL |
| B | TPU sleeve | Thicker wall for a tighter fit. **Final version:** stopped the wheel from slipping on the shaft | SLDPRT |
| — | Logo insert | Extruded logo for the hub center | SLDPRT |

| Rev A: straight hub | Rev B: tapered hub |
|---|---|
| ![](renders/Wheel_tpu.png) | ![](renders/Wheel_tpu_Tapered.png) |

![TPU sleeve](renders/Wheel_tpu_sleeve.png)

## Manufacturing
| Part | Material | Why |
|---|---|---|
| Wheel | PETG | Tougher and more heat-resistant than PLA for a part that gets handled and gripped |
| TPU sleeve | TPU | Flexible, so the ribs compress for a friction fit and grip the shaft |
| Logo insert | PLA | Prints cleanly in multiple colors for the logo |

Splitting the design into three parts let each one use the material that suits its job, instead of compromising on one material for the whole wheel.

## Results
- The tapered hub (Rev B) printed more reliably and needed less support than the straight hub (Rev A).
- The original sleeve let the wheel slip on the shaft. The thicker sleeve (Rev B) gave a tighter fit and stopped the slipping, so it's the final design.

<!-- TODO: add photos of the printed and installed wheel to renders/ and link them here -->

## Files
- Native SolidWorks parts: [`cad/`](cad)
- STL files: [`exports/`](exports)
- Renders: [`renders/`](renders)
