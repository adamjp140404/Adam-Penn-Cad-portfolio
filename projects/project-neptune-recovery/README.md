# Project Neptune: Recovery System

> 🚧 **Work in progress.** Project Neptune is an active, multi-year program. The designs and results here are preliminary and will change through testing, design reviews and the test flights.

![Sustainer main parachute opening-shock Monte Carlo](results/monte_carlo_sustainer_6ft.png)

**Team:** UCF AIAA × SEDS, [Project Neptune](https://www.ucfprojectneptune.com/) · **My role:** Recovery subteam: parachute opening-load analysis, and CAD mentor on the CO2 ejection system
**Tools:** Python (NumPy, SciPy, Matplotlib), SolidWorks

## About Project Neptune
Project Neptune is the joint engineering program of UCF's AIAA and SEDS student chapters, with technical guidance from UCF faculty and partner Seagate Space. The goal is a **two-stage, solid-fuel rocket that reaches at least 100 km**, making it UCF's first rocket to reach space. Seven subteams split the vehicle: Propulsion, Aerostructures, Recovery, Electronics, Systems, Test & Integration, and Logistics.

| Milestone | Date |
|---|---|
| Preliminary design review | Nov 2026 |
| First test launch, from an offshore barge off St. Petersburg, FL | May 2027 |
| Critical design review | Nov 2027 |
| Second sea launch | May 2028 |
| Final flight to space, from Nevada | ~Sep 2028 |

*Program summary and timeline from [ucfprojectneptune.com](https://www.ucfprojectneptune.com/).*

## My work on the recovery system
Each stage (booster and sustainer) recovers separately with a **drogue** deployed at apogee and a **main** deployed at 1,500 ft, so there are four parachutes. I worked on two parts of that system:

1. **[Parachute opening-load analysis](#parachute-opening-load-analysis):** Python tools that size each parachute to its descent-rate limit and predict its peak opening force.
2. **[CO2 ejection system](#co2-ejection-system):** I used this design as a hands-on CAD project to teach newer team members SolidWorks, walking them through modeling the parts and building the assembly.

## Parachute opening-load analysis
The **peak opening force** is the shock load when the canopy inflates. It sizes the shroud lines, the shock cord and the recovery hardware.

| Stage | Descent mass | Apogee (current test-flight inputs) |
|---|---|---|
| Sustainer | 23 lb | 23,000 ft |
| Booster | 27 lb | 11,000 ft |

### Method
Opening loads are calculated two independent ways, and the **higher** result is used for design:

- **Pflanz method:** force = steady drag × opening-force coefficient (Cx) × force reduction factor (X1). X1 is read from the Pflanz chart against the ballistic parameter A.
- **MIT method:** force = steady drag × opening shock factor (Ck). Ck is read from a fitted curve against the mass ratio Rm.

Inputs come from Knacke's *Parachute Recovery Systems Design Manual* (NWC TP 6575), with each choice documented in the code:

| Input | Value | Source |
|---|---|---|
| Opening-force coefficient Cx (main) | 1.3–1.7, best estimate 1.3–1.5 | Knacke Table 5-1 (annular is the closest canopy shape) |
| Canopy fill constant n | 4–14 sweep, 7–12 Monte Carlo | Knacke Table 5-6 |
| Pflanz drag-area curve | n = 2 | Knacke p. 5-58 (solid-cloth, unreefed canopy) |
| Gravity correction | +1 weight on Pflanz | Knacke p. 7-16 (vertical-descent openings) |
| Air density | ISA standard atmosphere at deployment altitude | |
| Main canopy | Rocketman Ultra-Light, Cd 2.2 | Manufacturer catalog |

**Two analyses for each parachute:**
1. **Size sweep:** every catalog size is checked against the descent-rate limit, and its opening-load range is found over a grid of Cx and fill-constant values.
2. **Monte Carlo:** 1,000,000 simulated openings with random line-stretch speed, drag area, air density, Cx and fill constant. The **95th-percentile (P95)** load is the design load.

### Results
| Parachute | Size | Descent rate | Design load (P95) | Load per line |
|---|---|---|---|---|
| Sustainer main | 6 ft Rocketman | 17.9 ft/s landing (limit 20) | 528 lbf | 44 lb of 220 lb rating |
| Booster main | 6 ft Rocketman | 19.4 ft/s landing (limit 20) | 551 lbf | 46 lb of 220 lb rating |
| Sustainer drogue | 20 in, Cd 0.97 | 97.8 ft/s at 1,500 ft (limit 100) | 113 lbf | 14 lb (8 lines, placeholder) |
| Booster drogue | 24 in, Cd 0.97 | 88.3 ft/s at 1,500 ft (limit 100) | 219 lbf | 27 lb (8 lines, placeholder) |

Loads are before a safety factor. The booster main meets its 20 ft/s limit with a thin margin; the 7 ft size lands at 16.6 ft/s if more margin is needed.

| Booster main, 6 ft | Sustainer drogue, 20 in | Booster drogue, 24 in |
|---|---|---|
| ![](results/monte_carlo_booster_6ft.png) | ![](results/drogue_monte_carlo_sustainer_20in.png) | ![](results/drogue_monte_carlo_booster_24in.png) |

Each plot shows the distribution of peak opening force from both methods (left) and how the Pflanz P95 load grows with Cx (right). Full sweep tables for all sizes are in [`results/`](results).

### What I built on the original code
The Pflanz and MIT chart data and interpolation functions come from Carlos Albiñana Burdiel's open-source [Parachute-Opening-Shock](https://github.com/CarlosAlbi/Parachute-Opening-Shock) repository (MIT License; see [`code/LICENSE-Parachute-Opening-Shock`](code/LICENSE-Parachute-Opening-Shock)). I adapted it to this mission and fixed several problems found while testing:

- **Fixed the nominal-diameter formula.** The example used a hard-coded D0; it is now calculated from the canopy area.
- **Guarded the chart limits.** Cases outside the digitized Pflanz and MIT charts were extrapolating to unrealistic or negative loads; they are now excluded and flagged.
- **Fixed the Monte Carlo MIT inputs.** The MIT term now uses each sample's velocity and drag area instead of fixed values, so it reflects the full uncertainty.
- **Fixed invalid MIT values.** Cases with a generalized fill constant below 1 returned uninitialized numbers; they are now marked invalid.
- **Added** the Knacke-based input choices, gravity correction, standard-atmosphere density, the Rocketman catalog, booster and sustainer stage profiles, the all-sizes Monte Carlo table, a mass table and a command-line interface.

Every line of the scripts is labeled `[REPO]`, `[MODIFIED]` or `[ADDED]`, so it's clear which code is original and which is mine.

## CO2 ejection system
**Files:** [`cad/co2-ejection/`](cad/co2-ejection) (SolidWorks assembly and 6 parts)

![CO2 ejection system section view](renders/co2-section-view.png)

| Charge end | Outlet end |
|---|---|
| ![](renders/co2-iso-charge-end.png) | ![](renders/co2-iso-outlet-end.png) |

The CO2 ejection system ("Sparrow") uses a CO2 cartridge to pressurize the airframe and deploy the parachutes. As the section view shows:

1. **Charge cup** (left, black): holds a small pyrotechnic charge, fired electrically through the two wire ports.
2. **Cartridge** (gold): sits in a holder, held back from the puncture pin by a spring (the helix).
3. **Firing:** the charge drives the cartridge forward against the spring and onto the fixed, cone-tipped **puncture pin** (right).
4. **Release:** the CO2 escapes through the vent holes in the threaded outlet end, which mounts through a bulkhead.

**My role: CAD mentor.** I used the ejection system as a training project for newer recovery-team members, teaching them SolidWorks and walking them through designing each part and building the assembly. The assembly was modeled by the team under that guidance. It gave new members real flight hardware to learn on instead of practice exercises.

**Why CO2:** compared with a black-powder charge pressurizing the airframe directly, CO2 gives more consistent ejection, is simple to use, and the cartridges and hardware are easy to buy off the shelf.

The assembly includes:

| Part | File |
|---|---|
| Outer body | `Sparrow (Outer).SLDPRT` |
| Outer top shell | `Sparrow Outer Top Shell - Part 1.SLDPRT` |
| CO2 cartridge and helix holder | `Sparrow (CO2 and Helix holder).SLDPRT` |
| CO2 cartridge top | `Sparrow (Top of CO2 can).SLDPRT` |
| Puncture pin | `Sparrow (Pin).SLDPRT` |
| Charge cup | `Sparrow Charge Cup - Part 1.SLDPRT` |

## Next steps
- Finish and test the CO2 ejection system.
- Replace the drogue placeholders with real values: line-stretch speed from the trajectory simulation, and Cx, line count and line rating once the drogue type is chosen.
- Apply a safety factor and size the shock cord and hardware.
- Compare predictions with measured loads from the May 2027 test flight.

## Files
- CO2 ejection system CAD: [`cad/co2-ejection/`](cad/co2-ejection)
- Code and run instructions: [`code/`](code)
- Monte Carlo plots and sweep tables: [`results/`](results)
- Quick reference (commands, settings, results): [`docs/Parachute_Code_Quick_Reference.pdf`](docs/Parachute_Code_Quick_Reference.pdf)
