# =============================================================================
# drogue_sweep.py
# DROGUE sizing and opening-shock sweep. Copy of main_chute_sweep.py adapted for
# the drogue (separate file so the main-chute results are untouched).
#
# Differences from main_chute_sweep.py:
#   - sizes are drogue diameters in INCHES, Cd 0.97 referenced to full-diameter area
#   - deployment at apogee (23,000 ft); line-stretch speed is a placeholder
#   - descent check is the drogue speed at MAIN DEPLOYMENT altitude (1500 ft),
#     not landing speed at sea level
#   - Cx / line count are placeholders until the drogue type is known
#   - the calculations (Pflanz, MIT, Monte Carlo) are identical to the main script
#
# PROVENANCE LABELS used throughout this file:
#   [REPO: <file>]     taken from that file in the repository, unchanged
#   [MODIFIED: <file>] based on that file, changed as described
#   [ADDED]            new code, not in the repository
#
# Needs interpolating_functions.py and combined_data.pkl in the same folder.
# Add --booster or --sustainer (default) to any command to pick the stage.
# Run:  python drogue_sweep.py                    -> sweep of all drogue sizes
#       python drogue_sweep.py --monte-carlo      -> Monte Carlo for MC_SIZE_IN
#       python drogue_sweep.py --monte-carlo-all  -> Monte Carlo P95 for every size
#       python drogue_sweep.py --mass-table       -> smallest OK drogue vs mass
# =============================================================================

import pickle
import numpy as np

# [REPO: interpolating_functions.py] - both functions imported and used unchanged
from interpolating_functions import evaluate_pflanz, evaluate_mit

# ============================ USER INPUTS ====================================
# [MODIFIED: SingleValue_Example.py] - same kind of parameter block, but with your
# mission values in imperial units (converted to SI below)
# [ADDED] Stage profiles. Pick one at the command line:
#     python drogue_sweep.py --booster        (or --sustainer, the default)
# Each profile sets the inputs below. Edit the numbers here to change a stage.
#   MASS_LB          mass under the drogue                          [lb]
#   DEPLOY_FT        drogue deployment altitude (apogee)            [ft]
#   V_DEPLOY_FPS     velocity at drogue line stretch. At apogee the vertical
#                    speed is ~0, but residual horizontal speed and the fall during
#                    ejection/line stretch (~32 ft/s per second of delay) add to it.
#                    PLACEHOLDER (150 = conservative) - replace with sim value [ft/s]
#   MAX_DESCENT_FPS  max drogue descent rate, checked at DESCENT_CHECK_FT [ft/s]
#   DESCENT_CHECK_FT altitude where the descent rate is checked (main deploy) [ft]
#   MC_SIZE_IN       drogue diameter analyzed by --monte-carlo      [in]
#   MC_V_MEAN_FPS    Monte Carlo mean line-stretch velocity (PLACEHOLDER) [ft/s]
STAGE = "sustainer"        # default stage when no flag is given
STAGES = {
    "sustainer": dict(MASS_LB=23.0, DEPLOY_FT=23000, V_DEPLOY_FPS=150, MAX_DESCENT_FPS=100,
                      DESCENT_CHECK_FT=1500, MC_SIZE_IN=20, MC_V_MEAN_FPS=150.0),
    "booster":   dict(MASS_LB=27.0, DEPLOY_FT=11000, V_DEPLOY_FPS=150, MAX_DESCENT_FPS=100,
                      DESCENT_CHECK_FT=1500, MC_SIZE_IN=24, MC_V_MEAN_FPS=150.0),
}
globals().update(STAGES[STAGE])

# All references below are to Knacke, Parachute Recovery Systems Design Manual,
# NWC TP 6575 (the manual linked in the repo README).

# [ADDED] Opening force coefficient at infinite mass, Cx. PLACEHOLDER until the
# drogue canopy type is known. 1.4-1.8 spans the solid canopies in Knacke
# Table 5-1 (extended skirt / annular ~1.4, hemispherical ~1.6, flat circular
# ~1.7, conical ~1.8). The drogue is in the "infinite mass" regime, so its
# Pflanz load is ~Cx x steady drag: Cx matters much more here than for the main.
CX_RANGE      = (1.4, 1.8)  # opening force coefficient, infinite mass [-]

# [ADDED] Highlighted band. Set to the Knacke Table 5-1 value for your drogue
# type once known (e.g. flat circular ~1.7 -> (1.6, 1.8)).
CX_CORE_RANGE = (1.6, 1.8)  # best-estimate band (placeholder)          [-]
CX_CORE_LABEL = "placeholder - set for drogue type"

# [ADDED] Canopy fill constant, n, in tf = n*D0/v.
# Knacke Table 5-6 (p. 5-44) does NOT list the annular type. 4-14 spans every
# UNREEFED parachute type in that table (ribless guide surface 4-6 ... ribbon and
# ringslot 14), so the sweep brackets all tabulated canopies. Note the table's
# formula was fitted to ~150-500 ft/s; our 100 ft/s is below that range.
# MIT's force steps up at nfill ~ 8 for this chute; Pflanz is highest at low nfill.
# Previous (unsourced) value: NFILL_RANGE = (6.0, 12.0)
NFILL_RANGE = (4.0, 14.0)   # canopy fill constant                      [-]

# [MODIFIED: SingleValue_Example.py] Pflanz drag-area growth curve.
# Knacke p. 5-58: n = 2 (concave) represents solid cloth parachutes; n = 1 is
# ribbon/ringslot; n = 0.5 (convex) occurs only in REEFED inflation of
# extended-skirt parachutes. Rocketman's canopy is solid cloth and unreefed.
# Repo default was '0.5'; previous version of this script used ("0.5", "1", "2").
# To be more conservative, use ("0.5", "2") - n = 0.5 gives the highest forces.
PFLANZ_CASES = ("2",)

# [ADDED] Gravity correction for Pflanz.
# Knacke p. 7-16: Pflanz neglects gravity; parachutes opened in vertical descent
# see a force one weight unit higher than calculated. Applied to Pflanz only
# (MIT is built from test data, and the manual's note is specific to Pflanz).
PFLANZ_ADD_WEIGHT = True

# [ADDED] range of the digitized Pflanz chart (Knacke Fig. 5-51 / repo data)
PFLANZ_A_MIN, PFLANZ_A_MAX = 0.01, 1000.0
# =============================================================================

# [ADDED] unit conversions
LB2KG, FT2M, LBF2N = 0.45359237, 0.3048, 4.4482216

# [ADDED] Drogue sizes. Cd 0.97 is assumed to be referenced to the full-diameter
# area (pi*D^2/4); check this against the drogue's spec sheet.
DROGUE_SIZES_IN = (12, 15, 18, 20, 24, 30, 36)   # diameters to sweep      [in]
DROGUE_LINES    = 8     # number of shroud lines (PLACEHOLDER)
LINE_RATING_LB  = 220   # line rating, lb (PLACEHOLDER - set to your drogue's)
CD_PROJ = 0.97          # drogue Cd (variable name kept from the main script)

# size [in], reference area [ft^2], nominal area [ft^2], number of lines
CATALOG = [(d, np.pi * (d / 12) ** 2 / 4, np.pi * (d / 12) ** 2 / 4, DROGUE_LINES)
           for d in DROGUE_SIZES_IN]


def isa_density(alt_m):
    """[ADDED] ISA troposphere density [kg/m^3], valid up to 11 km (36,089 ft).
    (The repo hard-codes atm_density = 1.18.)"""
    if alt_m > 11000:
        raise ValueError("isa_density is only valid up to 36,089 ft")
    return 1.225 * (1 - 2.25577e-5 * alt_m) ** 4.25588


def opening_loads(data, mass, rho, v, CdS, S0):
    """Return (pflanz_min, pflanz_max, mit_min, mit_max) peak opening force [N]."""

    # [MODIFIED: SingleValue_Example.py] repo line: D0 = 4*np.sqrt(12/np.pi)
    # Fixed to the circular-canopy formula, using the canopy (cloth) area
    D0 = np.sqrt(4 * S0 / np.pi)

    # [ADDED] grid over the uncertain Cx and nfill values
    cx, nf = np.meshgrid(np.linspace(*CX_RANGE, 17), np.linspace(*NFILL_RANGE, 21))
    cx, nf = cx.ravel(), nf.ravel()

    # [REPO: SingleValue_Example.py] force_nominal = 0.5*atm_density*(v_ls**2)*S0*CD0
    # (written with the product CdS = S0*CD0)
    F_ss = 0.5 * rho * v**2 * CdS

    # [REPO: SingleValue_Example.py] tf = nfill*D0/v_ls
    tf = nf * D0 / v

    # [REPO: SingleValue_Example.py] A_ballistic = 2*mass/(S0*CD0*atm_density*v_ls*tf)
    A = 2 * mass / (CdS * rho * v * tf)

    # [REPO: SingleValue_Example.py] Pflanz force = force_nominal * Cx * X1
    # (looped over all three curves instead of only '0.5')
    pflanz = np.concatenate([F_ss * cx * evaluate_pflanz(data, c, A) for c in PFLANZ_CASES])

    # [ADDED] Knacke p. 7-16: +1 weight unit for vertical-descent openings
    if PFLANZ_ADD_WEIGHT:
        pflanz = pflanz + mass * 9.80665

    # [ADDED] the Pflanz chart was digitized for 0.01 <= A <= 1000 only. Outside
    # that, the interpolator extrapolates (gave unrealistic values for large
    # chutes), so those cases are excluded. pf_frac = share of cases on the chart.
    A_all = np.tile(A, len(PFLANZ_CASES))
    on_chart = (A_all >= PFLANZ_A_MIN) & (A_all <= PFLANZ_A_MAX)
    pflanz = np.where(on_chart, pflanz, np.nan)
    pf_frac = on_chart.mean()

    def _rng(x):
        return (np.nanmin(x), np.nanmax(x)) if np.isfinite(x).any() else (np.nan, np.nan)

    pmin, pmax = _rng(pflanz)

    # [ADDED] same Pflanz result restricted to the highlighted Cx band
    cx_all = np.tile(cx, len(PFLANZ_CASES))
    in_core = (cx_all >= CX_CORE_RANGE[0] - 1e-9) & (cx_all <= CX_CORE_RANGE[1] + 1e-9)
    pcore = _rng(pflanz[in_core])

    # [REPO: SingleValue_Example.py] Rm = atm_density*(S0*CD0)**(3/2)/mass
    Rm = rho * CdS**1.5 / mass

    # [ADDED] the MIT chart was digitized for 1e-4 <= Rm <= 10 only. Outside that,
    # the repo would extrapolate the polynomial (it went negative in testing),
    # so MIT is skipped and only Pflanz is reported.
    if not (1e-4 <= Rm <= 10):
        return pmin, pmax, np.nan, np.nan, pf_frac, pcore

    # [REPO: SingleValue_Example.py] drag-integral choice
    #   if Rm > 0.1: 0.5   elif Rm > 0.01: (0.5+0.2)/2   else: 0.2
    DI = 0.5 if Rm > 0.1 else (0.35 if Rm > 0.01 else 0.2)

    # [REPO: SingleValue_Example.py] n_gen_fill = v_ls*tf*Drag_integral/np.sqrt(S0*CD0)
    n_gen = v * tf * DI / np.sqrt(CdS)

    # [REPO: interpolating_functions.py] evaluate_mit, called unchanged
    ck = evaluate_mit(data, n_gen, np.full_like(n_gen, Rm))

    # [ADDED] evaluate_mit leaves uninitialized values where n_gen < 1;
    # mark those as invalid instead of using them
    ck = np.where(n_gen >= 1, ck, np.nan)

    # [REPO: SingleValue_Example.py] MIT force = force_nominal * Ck
    mit = F_ss * ck
    return pmin, pmax, np.nanmin(mit), np.nanmax(mit), pf_frac, pcore


def sweep(data, mass_lb, verbose=True):
    """[ADDED] Run the opening-load calculation for every catalog size."""
    mass = mass_lb * LB2KG
    rho_dep = isa_density(DEPLOY_FT * FT2M)
    rho_land = isa_density(DESCENT_CHECK_FT * FT2M)   # drogue speed at main deployment
    v = V_DEPLOY_FPS * FT2M
    rows = []
    for size, a_proj, a_can, n_lines in CATALOG:
        # [ADDED] drag area from Rocketman's projected-area Cd; S0 from cloth area
        CdS = CD_PROJ * a_proj * FT2M**2
        S0 = a_can * FT2M**2

        # [ADDED] terminal descent rate: W = 0.5*rho*v^2*CdS
        v_land = np.sqrt(2 * mass * 9.80665 / (rho_land * CdS)) / FT2M

        pmin, pmax, mmin, mmax, pf_frac, pcore = opening_loads(data, mass, rho_dep, v, CdS, S0)
        both = np.array([pmax, mmax])
        worst_lbf = np.nanmax(both) / LBF2N if np.isfinite(both).any() else np.nan
        rows.append(dict(size=size, v_land=v_land, pmin=pmin / LBF2N, pmax=pmax / LBF2N, pf_frac=pf_frac,
                         pcmin=pcore[0] / LBF2N, pcmax=pcore[1] / LBF2N,
                         mmin=mmin / LBF2N, mmax=mmax / LBF2N,
                         per_line=worst_lbf / n_lines, n_lines=n_lines))
    if verbose:
        print(f"\nMass {mass_lb:.1f} lb | deploy {V_DEPLOY_FPS} ft/s @ {DEPLOY_FT} ft "
              f"(rho {rho_dep:.3f} kg/m^3) | descent checked at {DESCENT_CHECK_FT} ft")
        print(f"Cx {CX_RANGE} | nfill {NFILL_RANGE} | Pflanz curve(s) {PFLANZ_CASES}"
              f"{' + weight (gravity)' if PFLANZ_ADD_WEIGHT else ''}")
        print(f">> Highlighted column: Pflanz with Cx {CX_CORE_RANGE[0]}-{CX_CORE_RANGE[1]} "
              f"({CX_CORE_LABEL}, Knacke Table 5-1)\n")
        hl = f">>Cx {CX_CORE_RANGE[0]}-{CX_CORE_RANGE[1]}<<"
        print(f"{'Size':>5} {'Descent':>8} {'Pflanz, full Cx':>17} {hl:>17} "
              f"{'MIT [lbf]':>15} {'Worst/line':>11}  OK?")

        def band(lo, hi, w=15):
            return f"{lo:>6.0f} - {hi:<6.0f}" if np.isfinite(lo) else f"{'n/a':>{w}}"

        for r in rows:
            ok = "yes" if r["v_land"] <= MAX_DESCENT_FPS else "too fast"
            star = "*" if 0 < r["pf_frac"] < 1 else " "
            pf = band(r["pmin"], r["pmax"]) + star
            pc = band(r["pcmin"], r["pcmax"]) + star
            mit = band(r["mmin"], r["mmax"]) if np.isfinite(r["mmin"]) else f"{'n/a (Rm>10)':>15}"
            line = (f"{r['per_line']:>7.0f} lb" if np.isfinite(r["per_line"]) else f"{'n/a':>10}")
            print(f"{r['size']:>3}in {r['v_land']:>6.1f}fps  {pf}  {pc}  {mit} {line}   {ok}")
        print("\nMIT does not use Cx, so its column is the same for any Cx range.")
        if any(r["pf_frac"] < 1 for r in rows):
            print("\n* Part of the nfill range puts the Pflanz ballistic parameter A below the "
                  "chart (A < 0.01); those cases are left out of the Pflanz range.")
        print(f"\nLines: {DROGUE_LINES} (placeholder), rating {LINE_RATING_LB} lb each (placeholder). 'Worst/line' assumes the load "
              "splits evenly across lines, with no safety factor.")
    return rows


# =============================================================================
# MONTE CARLO SECTION
# [MODIFIED: RangeValues_Example.py] - same approach as the repo's range example
# (random samples of the uncertain inputs, vectorized Pflanz + MIT, histograms,
# average and percentile loads), adapted to the Rocketman chute and with these
# fixes:
#   - D0 from the canopy cloth area (repo used D0 = 4*np.sqrt(12/np.pi))
#   - n_gen_fill uses the SAMPLED velocity and drag area (repo used the fixed
#     v_ls and CD0, so MIT ignored part of the uncertainty)
#   - velocity samples are truncated so speed can't go to zero or negative
#   - all three Pflanz curves are sampled, not only '0.5'
#   - MIT samples outside the digitized chart (n_gen < 1, Rm outside 1e-4..10)
#     are excluded instead of returning garbage/extrapolated values
# This section only runs with:  python main_chute_sweep.py --monte-carlo
# It does not change the normal sweep output.
# =============================================================================

# ------------------------ MONTE CARLO INPUTS ---------------------------------
# MC_SIZE_IN (drogue diameter to analyze) is set per stage in STAGES at the top.
MC_SAMPLES   = 1_000_000   # number of random cases (repo: N = 1000000)
MC_SEED      = 42          # fixed seed so results repeat; None = new each run

# Uncertain inputs (ASSUMED distributions - update these with test data)
# MC_V_MEAN_FPS (mean drogue line-stretch speed) is set per stage in STAGES.
MC_V_SIGMA_FPS = 40.0      # wide spread until the sim gives a value   [ft/s]
MC_V_MIN_FPS   = 10.0      # truncation: no samples below this         [ft/s]
MC_CD_FACTOR   = (0.9, 1.1)          # uniform scatter on the drogue CdS [-]
MC_RHO_RANGE   = (0.97 * isa_density(DEPLOY_FT * FT2M), isa_density(DEPLOY_FT * FT2M))  # hot day (-3%) .. standard at deploy altitude [kg/m^3]
MC_CX_RANGE    = CX_RANGE            # same as the sweep (1.3-1.7)      [-]
# Kept narrower than the sweep on purpose: the Monte Carlo treats every value in
# the range as equally likely, and 7-12 spans the solid-canopy types in Knacke
# Table 5-6 (flat circular 8, extended skirt 10-12, ringsail 7). The sweep's
# wider 4-14 range covers the envelope of all tabulated types.
MC_NFILL_RANGE = (7.0, 12.0)         # solid canopies, uniform          [-]
MC_PERCENTILES = (95, 99)
# -----------------------------------------------------------------------------


def monte_carlo(data, mass_lb=MASS_LB, size_ft=MC_SIZE_IN, show_plots=True, quiet=False):
    """Run the Monte Carlo for one size. quiet=True skips printing and plots and
    just returns the summary numbers (used by the all-sizes table)."""
    rng = np.random.default_rng(MC_SEED)
    N = MC_SAMPLES

    entry = next((c for c in CATALOG if c[0] == size_ft), None)
    if entry is None:
        raise ValueError(f"No {size_ft} in drogue in DROGUE_SIZES_IN")
    _, a_proj, a_can, n_lines = entry

    mass = mass_lb * LB2KG
    S0 = a_can * FT2M**2
    D0 = np.sqrt(4 * S0 / np.pi)                          # fixed D0 formula

    # [MODIFIED: RangeValues_Example.py] sampled inputs
    v = rng.normal(MC_V_MEAN_FPS, MC_V_SIGMA_FPS, N)
    bad = v < MC_V_MIN_FPS                                # truncate low tail
    while bad.any():
        v[bad] = rng.normal(MC_V_MEAN_FPS, MC_V_SIGMA_FPS, bad.sum())
        bad = v < MC_V_MIN_FPS
    v = v * FT2M
    CdS = CD_PROJ * a_proj * FT2M**2 * rng.uniform(*MC_CD_FACTOR, N)
    rho = rng.uniform(*MC_RHO_RANGE, N)
    cx = rng.uniform(*MC_CX_RANGE, N)
    nf = rng.uniform(*MC_NFILL_RANGE, N)
    curve = rng.choice(np.array(PFLANZ_CASES), N)         # Pflanz curve per sample

    # [REPO: RangeValues_Example.py] same formulas, element-wise on the arrays
    tf = nf * D0 / v                                      # fill time
    A = 2 * mass / (CdS * rho * v * tf)                   # ballistic parameter
    Rm = rho * CdS**1.5 / mass                            # mass ratio
    DI = np.where(Rm > 0.1, 0.5, np.where(Rm > 0.01, (0.5 + 0.2) / 2, 0.2))
    n_gen = v * tf * DI / np.sqrt(CdS)                    # fixed: sampled v and CdS
    F_ss = 0.5 * rho * v**2 * CdS                         # steady drag

    # Pflanz: force = F_ss * Cx * X1
    X1 = np.empty(N)
    for c in PFLANZ_CASES:
        m = curve == c
        X1[m] = evaluate_pflanz(data, c, A[m])
    pflanz = F_ss * cx * X1
    if PFLANZ_ADD_WEIGHT:                                 # Knacke p. 7-16
        pflanz = pflanz + mass * 9.80665
    pflanz = pflanz / LBF2N
    pflanz = np.where((A >= PFLANZ_A_MIN) & (A <= PFLANZ_A_MAX), pflanz, np.nan)

    # MIT: force = F_ss * Ck, only where the chart is valid
    valid = (n_gen >= 1) & (Rm >= 1e-4) & (Rm <= 10)
    mit = np.full(N, np.nan)
    if valid.any():
        mit[valid] = F_ss[valid] * evaluate_mit(data, n_gen[valid], Rm[valid]) / LBF2N

    # ------------------------------ RESULTS ----------------------------------
    def stats(x):
        x = x[np.isfinite(x)]
        if x.size == 0:
            return x, [np.nan] * (len(MC_PERCENTILES) + 2)
        return x, [np.mean(x)] + [np.percentile(x, p) for p in MC_PERCENTILES] + [np.max(x)]

    core = (cx >= CX_CORE_RANGE[0]) & (cx <= CX_CORE_RANGE[1])

    if quiet:
        _, ps = stats(pflanz)
        _, pcs = stats(pflanz[core])
        _, ms = stats(mit)
        p95 = [ps[1], ms[1]]
        design = np.nanmax(p95) if np.isfinite(p95).any() else np.nan
        return dict(size=size_ft, pflanz_p95=ps[1], pflanz_core_p95=pcs[1],
                    mit_p95=ms[1], design=design,
                    per_line=design / n_lines, mit_valid=valid.mean(),
                    pflanz_valid=np.isfinite(pflanz).mean())

    sweep_row = next(r for r in sweep(data, mass_lb, verbose=False) if r["size"] == size_ft)

    print("\n================ MONTE CARLO (RangeValues method) ================")
    print(f"{size_ft} in drogue | mass {mass_lb:.1f} lb | {N:,} samples | seed {MC_SEED}")
    print(f"Velocity ~ N({MC_V_MEAN_FPS:.0f}, {MC_V_SIGMA_FPS:.0f}) ft/s, >= {MC_V_MIN_FPS:.0f} | "
          f"Cx {MC_CX_RANGE} | nfill {MC_NFILL_RANGE} | CdS x{MC_CD_FACTOR} | rho ({MC_RHO_RANGE[0]:.3f}, {MC_RHO_RANGE[1]:.3f})")
    hdr = "".join(f"{f'P{p}':>9}" for p in MC_PERCENTILES)
    print(f"\n{'Method':<22}{'Mean':>9}{hdr}{'Max':>9}   [lbf]")
    pf, pstats = stats(pflanz)
    print(f"{'Pflanz (Cx ' + str(MC_CX_RANGE[0]) + '-' + str(MC_CX_RANGE[1]) + ')':<22}"
          + "".join(f"{x:>9.0f}" for x in pstats))
    if len(PFLANZ_CASES) > 1:
        for c in PFLANZ_CASES:
            _, cs = stats(pflanz[curve == c])
            print(f"{'  Pflanz n = ' + c:<22}" + "".join(f"{x:>9.0f}" for x in cs))
    pfc, pcstats = stats(pflanz[core])
    print(f"{'>> Pflanz Cx ' + str(CX_CORE_RANGE[0]) + '-' + str(CX_CORE_RANGE[1]):<22}"
          + "".join(f"{x:>9.0f}" for x in pcstats)
          + f"   << {CX_CORE_LABEL} (Knacke Table 5-1)")
    if np.isfinite(mit).any():
        mf, mstats = stats(mit)
        print(f"{'MIT':<22}" + "".join(f"{x:>9.0f}" for x in mstats))
        print(f"  (MIT valid for {valid.mean()*100:.1f}% of samples)")
    else:
        mf, mstats = np.array([]), None
        print("MIT: no samples inside the chart range")

    design = max(pstats[1], mstats[1] if mstats else 0)   # higher of the two P95s
    print(f"\nDesign load at P{MC_PERCENTILES[0]} (higher method): {design:.0f} lbf"
          f"  ->  {design / n_lines:.0f} lb per line of {LINE_RATING_LB} lb rating")
    print(f"For comparison, sweep band for this size (min-max grid, v = {V_DEPLOY_FPS} ft/s):")
    print(f"  Pflanz {sweep_row['pmin']:.0f} - {sweep_row['pmax']:.0f} lbf | "
          f"MIT {sweep_row['mmin']:.0f} - {sweep_row['mmax']:.0f} lbf")
    print("Note: MC max can exceed the sweep max because velocity, CdS and density vary too.")

    # [MODIFIED: RangeValues_Example.py] histograms (Rice rule bins, as in the repo)
    # [ADDED] left: force histograms with the closest-shape Cx band overlaid;
    #         right: Pflanz force vs Cx with the closest-shape band shaded.
    import matplotlib.pyplot as plt
    num_bins = int(2 * N ** (1 / 3))
    core_lbl = f"Cx {CX_CORE_RANGE[0]}-{CX_CORE_RANGE[1]}: {CX_CORE_LABEL}"
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5),
                                  gridspec_kw={"width_ratios": [1.4, 1]})

    edges = np.histogram_bin_edges(np.concatenate([pf, mf]) if mf.size else pf, bins=num_bins)
    w = 1.0 / N / np.diff(edges)                          # common scale for all hists
    ax.hist(pf, bins=edges, weights=np.full(pf.size, w[0]), color="red", alpha=0.25,
            label=f"Pflanz, Cx {MC_CX_RANGE[0]}-{MC_CX_RANGE[1]}")
    ax.hist(pfc, bins=edges, weights=np.full(pfc.size, w[0]), histtype="step",
            color="darkred", lw=2, label=f"Pflanz, {core_lbl}")
    if mf.size:
        ax.hist(mf, bins=edges, weights=np.full(mf.size, w[0]), color="blue", alpha=0.3,
                label="MIT (does not use Cx)")
    ax.axvline(pstats[1], color="red", ls="--", lw=1,
               label=f"Pflanz P{MC_PERCENTILES[0]} = {pstats[1]:.0f}")
    ax.axvline(pcstats[1], color="darkred", ls="-.", lw=1.5,
               label=f"Pflanz P{MC_PERCENTILES[0]}, Cx {CX_CORE_RANGE[0]}-{CX_CORE_RANGE[1]}"
                     f" = {pcstats[1]:.0f}")
    if mstats:
        ax.axvline(mstats[1], color="blue", ls="--", lw=1,
                   label=f"MIT P{MC_PERCENTILES[0]} = {mstats[1]:.0f}")
    ax.set_xlabel("Peak opening force [lbf]")
    ax.set_ylabel("Probability density")
    ax.set_title(f"{STAGE.title()} drogue - opening shock Monte Carlo - {size_ft} in, {mass_lb:.0f} lb")
    ax.grid(True, ls="--", lw=0.5)
    ax.legend(fontsize=8)

    # Pflanz force vs Cx: median and P95 in Cx bins
    ok = np.isfinite(pflanz)
    cbins = np.linspace(*MC_CX_RANGE, 21)
    centers = 0.5 * (cbins[1:] + cbins[:-1])
    idx = np.digitize(cx[ok], cbins) - 1
    med = [np.median(pflanz[ok][idx == i]) if np.any(idx == i) else np.nan
           for i in range(len(centers))]
    p95 = [np.percentile(pflanz[ok][idx == i], MC_PERCENTILES[0]) if np.any(idx == i)
           else np.nan for i in range(len(centers))]
    ax2.axvspan(*CX_CORE_RANGE, color="gold", alpha=0.35, label=core_lbl)
    ax2.plot(centers, p95, "r-", lw=2, label=f"Pflanz P{MC_PERCENTILES[0]}")
    ax2.plot(centers, med, "r--", lw=1.5, label="Pflanz median")
    ax2.set_xlabel("Opening force coefficient Cx [-]")
    ax2.set_ylabel("Peak opening force [lbf]")
    ax2.set_title("Pflanz load vs Cx (Knacke Table 5-1)")
    ax2.set_xlim(*MC_CX_RANGE)
    ax2.grid(True, ls="--", lw=0.5)
    ax2.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    out = f"drogue_monte_carlo_{STAGE}_{size_ft}in.png"
    fig.savefig(out, dpi=150)
    print(f"\nHistogram saved to {out}")
    if show_plots:
        plt.show()


def smallest_ok_size(data, mass_lb):
    """[ADDED] Smallest catalog size meeting MAX_DESCENT_FPS, with its loads."""
    for r in sweep(data, mass_lb, verbose=False):
        if r["v_land"] <= MAX_DESCENT_FPS:
            return r
    return None


def mass_table(data, masses=range(10, 61, 5)):
    """[ADDED] For each descent mass, the smallest chute meeting the descent
    limit and its worst-case opening load from the sweep (min-max grid)."""
    print(f"\nSmallest size meeting <= {MAX_DESCENT_FPS} fps, by descent mass")
    print(f"Cx {CX_RANGE} | nfill {NFILL_RANGE} | Pflanz curve(s) {PFLANZ_CASES}"
          f"{' + weight' if PFLANZ_ADD_WEIGHT else ''} | deploy {V_DEPLOY_FPS} ft/s\n")
    print(f"{'Mass':>6} {'Size':>5} {'Descent':>8} {'Worst peak':>11} {'Worst/line':>11}")
    for m in masses:
        r = smallest_ok_size(data, m)
        if r is None:
            print(f"{m:>4}lb   none in catalog")
            continue
        both = np.array([r["pmax"], r["mmax"]])
        if np.isfinite(both).any():
            worst = np.nanmax(both)
            print(f"{m:>4}lb {r['size']:>3}in {r['v_land']:>6.1f}fps {worst:>8.0f} lbf "
                  f"{r['per_line']:>7.0f} lb")
        else:
            print(f"{m:>4}lb {r['size']:>3}in {r['v_land']:>6.1f}fps {'n/a':>12} {'n/a':>10}")
    print("\nWorst peak = higher of the Pflanz and MIT maximums from the sweep grid.")


def monte_carlo_all(data, mass_lb=MASS_LB):
    """[ADDED] Monte Carlo P95 table across every catalog size (same inputs as
    the single-size Monte Carlo, run once per size; no plots)."""
    rho_land = isa_density(DESCENT_CHECK_FT * FT2M)
    mass = mass_lb * LB2KG
    p = MC_PERCENTILES[0]
    print("\n============ MONTE CARLO - ALL SIZES (RangeValues method) ============")
    print(f"Mass {mass_lb:.1f} lb | {MC_SAMPLES:,} samples per size | seed {MC_SEED}")
    print(f"Velocity ~ N({MC_V_MEAN_FPS:.0f}, {MC_V_SIGMA_FPS:.0f}) ft/s | Cx {MC_CX_RANGE} | "
          f"nfill {MC_NFILL_RANGE} | Pflanz curve(s) {PFLANZ_CASES}"
          f"{' + weight' if PFLANZ_ADD_WEIGHT else ''}")
    print(f">> Highlighted column: Pflanz P{p} with Cx {CX_CORE_RANGE[0]}-{CX_CORE_RANGE[1]}"
          f" ({CX_CORE_LABEL}, Knacke Table 5-1)\n")
    print(f"{'Size':>5} {'Descent':>8} {f'Pflanz P{p}':>11} {'>>Cx core<<':>12} {f'MIT P{p}':>9} "
          f"{f'Design P{p}':>11} {'Per line':>9}  OK?")
    notes = set()
    for size, a_proj, _, _ in CATALOG:
        CdS = CD_PROJ * a_proj * FT2M**2
        v_land = np.sqrt(2 * mass * 9.80665 / (rho_land * CdS)) / FT2M
        r = monte_carlo(data, mass_lb, size, show_plots=False, quiet=True)
        def fmt(x, w, flag=""):
            return f"{x:>{w}.0f}{flag}" if np.isfinite(x) else f"{'n/a':>{w}} "
        pf_flag = "*" if 0 < r["pflanz_valid"] < 1 else " "
        mit_flag = "+" if 0 < r["mit_valid"] < 1 else " "
        if pf_flag == "*": notes.add("*")
        if mit_flag == "+": notes.add("+")
        if not np.isfinite(r["mit_p95"]): notes.add("mit")
        if not np.isfinite(r["pflanz_p95"]): notes.add("pf")
        ok = "yes" if v_land <= MAX_DESCENT_FPS else "too fast"
        per_line = f"{r['per_line']:>6.0f} lb" if np.isfinite(r["per_line"]) else f"{'n/a':>9}"
        print(f"{size:>3}in {v_land:>6.1f}fps {fmt(r['pflanz_p95'], 10, pf_flag)} "
              f"{fmt(r['pflanz_core_p95'], 11, pf_flag)} "
              f"{fmt(r['mit_p95'], 8, mit_flag)} {fmt(r['design'], 10)} {per_line}  {ok}")
    print()
    if "*" in notes:
        print("* Some Pflanz samples fell off the chart (A < 0.01) and were left out.")
    if "pf" in notes:
        print("Pflanz n/a: the whole sample range is off the Pflanz chart (A < 0.01).")
    if "+" in notes:
        print("+ Some MIT samples fell outside the MIT chart and were left out.")
    if "mit" in notes:
        print("MIT n/a: mass ratio Rm > 10, outside the MIT chart; design uses Pflanz only.")
    print(f"Design = higher of the two P{p} values. Per line assumes an even split, "
          f"no safety factor; line rating {LINE_RATING_LB} lb.")


def apply_stage(name):
    """[ADDED] Load one stage profile from STAGES into the module settings."""
    g = globals()
    g.update(STAGES[name])
    g["STAGE"] = name
    g["MC_RHO_RANGE"] = (0.97 * isa_density(g["DEPLOY_FT"] * FT2M),
                         isa_density(g["DEPLOY_FT"] * FT2M))


if __name__ == "__main__":
    import sys

    # [REPO: SingleValue_Example.py] load the interpolator data from the pickle
    with open("combined_data.pkl", "rb") as f:
        data = pickle.load(f)

    # [ADDED] command-line options: a stage flag and/or a mode flag, in any order
    #   python drogue_sweep.py [--booster | --sustainer] [--monte-carlo | --monte-carlo-all | --mass-table]
    args = [a.lstrip("-").lower() for a in sys.argv[1:]]
    unknown = [a for a in args if a not in STAGES and a not in ("monte-carlo", "monte-carlo-all", "mass-table")]
    if unknown:
        sys.exit(f"Unknown option(s): {', '.join(unknown)}. Stages: {', '.join(STAGES)}; "
                 "modes: --monte-carlo, --monte-carlo-all, --mass-table")
    stage = next((a for a in args if a in STAGES), STAGE)
    apply_stage(stage)
    print(f"\n########## {stage.upper()} DROGUE ##########")

    if "monte-carlo" in args:
        monte_carlo(data, MASS_LB, MC_SIZE_IN)
    elif "monte-carlo-all" in args:
        monte_carlo_all(data, MASS_LB)
    elif "mass-table" in args:
        mass_table(data)
    else:
        sweep(data, MASS_LB)
