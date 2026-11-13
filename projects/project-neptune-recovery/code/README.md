# Opening-shock code

Python scripts that size the four Project Neptune parachutes and estimate their peak opening loads.

| File | Purpose |
|---|---|
| `main_chute_sweep.py` | Main parachutes (booster and sustainer): size sweep, Monte Carlo, mass table |
| `drogue_sweep.py` | Drogue parachutes: same analyses, deployed at apogee |
| `SingleValue_Example.py` | One Pflanz and one MIT calculation for a hand check |
| `rebuild_pickle.py` | Builds `combined_data.pkl` (the digitized chart data) for your SciPy version |
| `interpolating_functions.py` | Pflanz and MIT chart interpolation, from [Parachute-Opening-Shock](https://github.com/CarlosAlbi/Parachute-Opening-Shock) (unchanged) |

Code from [Parachute-Opening-Shock](https://github.com/CarlosAlbi/Parachute-Opening-Shock) is used under the MIT License; see [`LICENSE-Parachute-Opening-Shock`](LICENSE-Parachute-Opening-Shock). Every line in the sweep scripts is tagged `[REPO]` (taken unchanged from the original repository), `[MODIFIED]` (based on it and changed), or `[ADDED]` (new).

## Setup
```
pip install -r requirements.txt
python rebuild_pickle.py
```

## Commands
Add `--booster` or `--sustainer` (the default) to any command.

```
python main_chute_sweep.py                    # size sweep: every main size
python main_chute_sweep.py --monte-carlo      # 1,000,000-sample Monte Carlo for MC_SIZE_FT; saves a plot
python main_chute_sweep.py --monte-carlo-all  # Monte Carlo P95 for every size
python main_chute_sweep.py --mass-table       # smallest passing main for 10-250 lb

python drogue_sweep.py                        # same options for the drogues
python SingleValue_Example.py                 # single hand-check calculation (forces in newtons)
```

Stage inputs (mass, deployment altitude, speeds, Monte Carlo size) are in the `STAGES` block at the top of each sweep script. See [`../docs/Parachute_Code_Quick_Reference.pdf`](../docs/Parachute_Code_Quick_Reference.pdf) for every setting and output term.
