# SAE Aero Design 2026: Micro Class

![UCF Team 310 aircraft at the 2026 SAE Aero Design competition](renders/photo-competition.jpg)

**Team:** UCF Knights Aero Design (Team 310), sponsored by Lockheed Martin · **My role:** Design, Manufacturing and CFD Lead
**Software:** SolidWorks, SolidWorks Simulation, ANSYS Fluent, XFLR5 · **Manufacturing:** laser-cut balsa, carbon fiber, FDM 3D printing

## Overview
A high-wing, electric RC aircraft designed for the 2026 SAE Aero Design **Micro Class**. The mission is to carry as much liquid payload (a 2 L water container) as possible under a **450 W power limit**, taking off within 100 ft. Each flight's score rewards payload, penalizes empty weight and wingspan, and adds a bonus for short takeoffs. That made weight, wing size and takeoff distance the main design drivers.

### Results
- **12th of 21** in Micro Class flight scoring
- **Completed every competition flight**
- Finished ahead of teams including international entries from India and Poland

| In flight at competition | Final configuration (CAD) |
|---|---|
| ![](renders/photo-in-flight.jpg) | ![](renders/aircraft-isometric.jpg) |

**Video:** [competition flight](docs/competition-flight.mp4), from the takeoff run through flight

| Parameter | Value |
|---|---|
| Configuration | High wing, conventional tail, fixed tricycle gear |
| Wingspan | 42 in (3.5 ft) |
| Chord | 21 in |
| Wing area | 882 in² (6.125 ft²) |
| Aspect ratio | 2:1 |
| Airfoil | NACA 6412 |
| Empty weight | 4.14 lb |
| Overall length | 57.25 in |
| Motor | Spektrum Avian 4250, 800 Kv |
| Propeller | APC 13 × 4 |
| Battery | 5000 mAh |
| Static margin | 11.9% loaded, 19.1% empty |
| Projected flight score | 41.0 (3 flights) |

![Top view planform](renders/aircraft-top-view.jpg)

## Design

### Wing sizing
**Files:** [`docs/Wing_Loading.xlsx`](docs/Wing_Loading.xlsx)

The wing was sized with a spreadsheet trade study that compares wings designed for cubic wing loadings from 3 to 9 and finds the takeoff speed and distance of each.

![Wing sizing trade study](renders/wing-sizing-trade-study.png)

**Method**
1. **Weight build-up:** component weights (payload, motor, battery, ESC, servos, receiver, propeller and fuselage) summed to a total aircraft weight.
2. **Wing area:** solved from the target cubic wing loading, *WCL = W / S^1.5*, then split into span and chord using a set aspect ratio.
3. **Lift coefficient:** CL against angle of attack, taken from XFLR5.
4. **Thrust:** estimated from the 450 W power limit using momentum (actuator disk) theory with a 13 in propeller and 70% efficiency, about 6.1 lbf.
5. **Takeoff speed:** *V = √(2W / ρSC_L)*.
6. **Takeoff distance:** constant-acceleration ground roll, *s = V² / 2g(T/W − μ)*, with a rolling friction coefficient of μ = 0.05.

**Result:** a lower wing loading gives a shorter takeoff but needs a bigger wing, which adds weight and a wingspan penalty to the score. A wing loading of 6 balanced the two. It gave the final 3.5 ft × 1.75 ft wing, which takes off at about **22 mph in about 13 ft** at 8° angle of attack, well within the 100 ft limit.

### Airfoil selection
An XFLR5 batch analysis compared candidate airfoils over Reynolds numbers up to 600,000 and angles of attack from −5° to 20°. NACA 6409, 6412 and 4612 gave the most lift at low Reynolds numbers. **NACA 6412** was selected because it has nearly the lift of the 6409 with less camber, which makes the aircraft less sensitive to changes in pitch stability.

![XFLR5 airfoil batch analysis](renders/xflr5-airfoil-batch.jpg)

### Payload and CG
The 2 L water container sits vertically in the fuselage near the center of gravity. That way, adding or removing payload barely moves the CG, which keeps trim consistent between loaded and empty flights, the same approach water bombers use. Internal **baffles** reduce sloshing, which would otherwise shift the CG and fight control inputs during the takeoff run.

<img src="renders/payload-container-baffles.jpg" width="300" alt="Payload container with baffles">

## Analysis

### CFD (ANSYS Fluent)
I ran the CFD to check lift at the critical takeoff condition: **30 ft/s at 8° angle of attack**. I modeled half the aircraft with a symmetry plane along the centerline, using a solid external shape because the finished aircraft is fully covered in film.

| Configuration | Lift (full aircraft) |
|---|---|
| Flaps neutral | ~3.0 lbf (12 N) |
| Flaps extended (takeoff setting) | **~7.0 lbf** |

Extending the flaps more than doubled lift at rotation speed. That confirmed the flaps as the main way to shorten the takeoff run.

| Flaps neutral | Flaps extended |
|---|---|
| ![](renders/cfd-neutral-flaps.jpg) | ![](renders/cfd-flaps-extended.jpg) |

### Structural FEA (SolidWorks Simulation)
The full aircraft structure was analyzed at a **critical load factor of n = 3**. A spanwise lift distribution was applied at the quarter-chord of the wing. Peak stresses stayed far below the strength of balsa, about 10 MPa. With that much margin, buckling of thin members, not material strength, is the more likely failure mode.

![FEA at critical load factor](renders/fea-critical-load-factor.jpg)

## Manufacturing
![Bare airframe before covering](renders/photo-airframe-skeleton.jpg)

*The airframe before covering: laser-cut balsa truss fuselage and tail boom, built-up rib-and-spar wing, 3D-printed nose cone and vertical stabilizer, and tricycle landing gear.*

![Structural exploded view](renders/structure-exploded-view.jpg)

- **Laser-cut 1/8 in balsa** for the ribs, spar slots and fuselage box-frame panels. Laser cutting keeps every rib profile identical, and parts were dry-fit before gluing.
- **Carbon fiber reinforcement** at the wing spars and wing-to-fuselage mounts, adding bending stiffness for little extra weight.
- **Heat-shrink film covering** for a smooth surface and added torsional stiffness.
- **FDM 3D printing** for complex parts, such as the vertical stabilizer below.
- **Aluminum landing gear struts and foam wheels.**

### Laser-cut balsa
**Files:** [`cad/laser-cut/`](cad/laser-cut), 16 cutting sheets with an [index](cad/laser-cut/README.md)

Every balsa part was nested onto 48 × 12 in sheets for the laser cutter: fuselage side, top and bottom panels, wing and tail ribs, spars, gussets, bulkheads and ailerons. The fuselage and tail panels are triangulated trusses, removing material where it carries little load and keeping the truss that does. The ribs and spars have lightening holes. Slots and tabs locate parts against each other during gluing. The set also includes revised panels and rebuild sheets cut during the build.

![Laser-cut sheets](renders/laser-cut-sheets.png)

### 3D-printed parts
**Files:** [`cad/printed-parts/`](cad/printed-parts)

Parts whose shapes are hard to make from flat balsa were printed in PLA on a Bambu Lab P1S:

![3D-printed parts](renders/printed-parts.png)

| Part | Size (mm) | Notes |
|---|---|---|
| Nose cone | 114 × 70 × 114 | Motor mount: holds the motor at the front of the fuselage through its 43 mm center opening, and fairs the square fuselage into a rounded nose to reduce drag |
| Tail side walls (left and right) | 100 × 108 × 6 | Mirrored pair. Lightened with triangular cutouts and finger-jointed to the balsa structure |
| Tail bottom | 78 × 9 × 114 | Finger-jointed panel closing the bottom of the tail section |
| Back brace | 58 × 15 × 30 | Connects all the tail parts together |

**Print settings (tail parts):** PLA, 0.08 mm layers, 2 walls, **8% infill**. Weight drives the empty-weight multiplier in the score, so the parts were printed as light as possible. The strength comes from the walls and the triangulated geometry, not the infill.


The printed tail parts use the same triangulated cutouts as the laser-cut balsa, and their finger joints slot straight into it. The printed and wood parts were designed to fit together as one structure.

### Vertical stabilizer with print-in-place rudder
**Files:** [`cad/vertical-stabilizer/`](cad/vertical-stabilizer)

![Vertical stabilizer: fin and rudder](renders/vertical-stabilizer.png)

The vertical stabilizer and its rudder print as **one piece** using a **print-in-place hinge**. The hinge prints already assembled, with a small clearance gap so it isn't fused, and the rudder can rotate as soon as it comes off the printer.

- **No assembly:** no separate hinge pins, tape hinges or glue joints between the fin and the rudder.
- **Fewer parts:** one print makes the whole tail surface, including the pushrod mount, so it's quick to reprint after a crash or to try a new design.
- **Simple design:** the hinge is part of the geometry, so the hinge line always stays aligned with the fin.
- **Control linkage:** the rudder has a built-in mounting point for the pushrod to the servo, so no separate control horn is needed.

**Result:** the stabilizer held up in flight and gave the rudder control the aircraft needed.

| Parameter | Value |
|---|---|
| Size | 202 mm chord × 82 mm tall × 28 mm thick |
| Hinge | Round hinge barrel along the hinge line. The fin and rudder are separate bodies with about 1 mm clearance |
| Material | PLA |
| Print settings | 0.2 mm layers, 2 walls, **5% infill**, tree supports (Bambu Lab P1S) |

The 5% infill keeps the tail light, which matters both for the empty-weight score multiplier and for balance, since weight at the tail has a long moment arm to the CG.


## Files
- Native SolidWorks parts: [`cad/`](cad)
- 3D-printed parts (STL and Bambu Studio project): [`cad/printed-parts/`](cad/printed-parts)
- Laser-cut sheets (DXF): [`cad/laser-cut/`](cad/laser-cut)
- Competition technical drawing: [`drawings/UCF_Aero_Design_Technical_Drawing.pdf`](drawings/UCF_Aero_Design_Technical_Drawing.pdf)
- Wing sizing spreadsheet: [`docs/Wing_Loading.xlsx`](docs/Wing_Loading.xlsx)

![Competition technical drawing](renders/technical-drawing.png)
