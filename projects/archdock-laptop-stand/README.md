# The ArchDock: Vertical Laptop / PC Stand

![ArchDock holding a laptop](renders/ArchDock_photo.jpg)

**Software:** SolidWorks, Bambu Studio · **Manufacturing:** FDM 3D printing (Bambu Lab P1S) · **Published:** [MakerWorld](https://makerworld.com/en/models/3443659-the-archdock-vertical-laptop-pc-stand)

## Overview
A vertical stand for a laptop or small PC, built from a continuous wave of rounded arches. The laptop stands on its long edge in the slot between the two rows of arches, which frees up desk space. The stand fits devices up to **1 in (25.4 mm)** thick. It prints in one piece with no supports and is published on MakerWorld for others to print.

Many printed vertical stands are too light to hold a laptop upright and need adhesive pads or tape to stay put. The ArchDock solves this with a weighted base: the bottom 28 mm prints at 40% infill instead of 15%, so it stays upright on its own.

**MakerWorld (as of Nov 2026):** 149 downloads · 37 prints · 38 likes · 164 collects · 5.0★ print profile rating · released Oct 15, 2026

## Design
| Feature | Dimension |
|---|---|
| Overall size (W × D × H) | 193.5 × 73.7 × 152.4 mm (7.6 × 2.9 × 6.0 in) |
| Form | Serpentine tube folded into two offset rows of arches, joined at the base |

The rounded arch tops are self-supporting, so the stand prints upright with no support material and has no sharp edges to scratch the laptop.

![ArchDock model views](renders/ArchDock.png)

## Print settings
| Setting | Value | Why |
|---|---|---|
| Printer | Bambu Lab P1S, 0.4 mm nozzle | |
| Material | PLA Matte | |
| Layer height | Variable, 0.08–0.28 mm | Thin layers on the curved arch tops to smooth out stair-stepping; thick layers on the straight sections to save time |
| Walls / infill | 2 walls, 15% grid infill | |
| Base infill | 40% in the bottom 28 mm (modifier) | Weights the base and lowers the center of gravity so the stand stays upright with a laptop in it. No adhesive or desk mounting needed |
| Supports | None | |
| Print time | ~9.8 h (~8.8 h with uniform 15% infill) | |

Two print profiles are published: the default with the 40% infill base, and a faster option with uniform 15% infill.

![ArchDock as sliced in Bambu Studio](renders/ArchDock_slicer.png)

## Files
- Native SolidWorks part: [`cad/ArchDock.SLDPRT`](cad)
- Print-ready Bambu Studio project, with all settings above: [`exports/ArchDock_BambuStudio.3mf`](exports)
- Mesh: [`exports/ArchDock.stl`](exports)
