# Robo_Vitruvian

Drive sizing for a humanoid arm across robot heights and payloads. For every height from
1.0 to 2.0 m and every payload in `config.toml` it scales the arm and picks the lightest
drive per joint (a motor module, direct or through a belt or capstan stage) that passes
torque, speed and size checks.

```
python run.py                           # summaries per payload, max payload, results/sweep.*
python run.py --height 1.8              # every payload at one height, all forces per joint
python run.py --height 1.8 --payload 5
python run.py --payload 3 --direct --exclude AKH70-16 --out results/3kg/direct
python -m pytest                        # or: uv run --group dev pytest
```

`--direct` drops the belt and capstan stages (module gearbox only). `--exclude [MOTOR ...]`
replaces the config's `exclude` and per-joint `allow` lists: the named motors go on no
joint, every other motor on every joint; `--exclude` alone allows every motor everywhere.
`--out` sets the output path without extension.

Python 3.11+ and openpyxl (for the workbook). All inputs are in `config.toml`, the motors
in `motors.toml`.

## Motors

`motors.toml` holds nine CubeMars modules, from the AK40-10 (190 g, 1.3 Nm rated) to the
AK10-9 (940 g, 18 Nm), every value from the specification tables on cubemars.com. Add
your own in the same format. Motors you can't publish go in `motors.local.toml` next to it:
it is gitignored, and when it exists every run adds its motors to the catalog and marks
them `local`. Outputs that use them then contain their data, so keep those private too.
`results/` and `private/` are gitignored.

## Outputs

`results/sweep.csv` has one row per payload and height (drive per joint, masses, what fails,
max payload at that height); `results/sweep-joints.csv` has every joint at every height and
payload, with shares as fractions (rated used 0.8 = 80%). `results/sweep.xlsx` holds the
same and more, every sheet with filters and a frozen header:
- **summary**: one row per payload and height, the drive per joint, masses, what fails
  and the max payload; infeasible rows red, a rule between payloads.
- **max payload**: heaviest payload any drive choice carries, per height.
- **joints N kg**: one sheet per payload, every joint at every height with forces,
  torques, use of rated and peak torque, speed and output diameter; heights banded,
  failing joints red.
- **motors**, **drive options**, **inputs**: what the run used.

## Model

- **Pose:** the arm stretched out horizontally, every joint treated as if its axis were
  horizontal and perpendicular to the arm. No pose loads a joint more, so this bounds
  every joint, and oversizes the roll joints (J3, J5, J7).
- **Joints:** J1–J3 at the shoulder, J4–J5 at the elbow, J6–J7 at the wrist. Each motor
  sits at its joint by default and loads only the joints before it.
- **Drives:** each motor direct, or with a belt (≤4:1 per stage, two stages) or capstan
  (≤8:1, one stage) after its gearbox. Torque at the joint = module torque × ratio ×
  efficiency. Total ratio (module gearbox × extra stage) ≤ 50:1 for backdrivability.
- **Motors per joint:** `exclude` keeps the AKH70-16 off the arm (it is meant for the
  legs); a joint's `allow` list lifts that, and J1–J3 allow it (the J1 motor sits in the
  torso and J2/J3 on the shoulder axis, so their mass loads no other arm joint).
- **Checks per joint:** holding torque ≤ 80% of rated; holding + acceleration torque ≤ 80%
  of peak; speed while holding ≥ the human 99th-percentile speed for that joint; output
  pulley or drum ≤ the limb diameter there. Acceleration: the joint alone gives the payload
  5 m/s². No Coriolis terms (zero speed at peak acceleration).
- **Speed:** the module's speed-torque line through its no-load and rated points at its
  datasheet voltage (24 or 48 V; the 48 V point where a sheet gives both; `max_V` raises
  it only where a datasheet allows more), divided by the extra ratio.
- **Output diameter:** the larger of stage ratio × input diameter and 2 × peak torque /
  allowed belt or cable tension.
- **Inertia:** links and hand as rods, drives and payload as points, plus the joint's own
  rotor through all its reduction (J_rotor · (gear ratio · extra ratio)²).
- **Masses:** link and hand structure from `config.toml`, scaled with height^1.5; motors
  from `motors.toml` plus 20% for brackets, driver and cabling; transmission per stage
  from `config.toml`.
- **Selection:** J7 first, working inwards, lightest drive that passes, which for a given
  motor and drive type is the smallest ratio that passes. A joint's load depends only on
  what lies beyond it, so this is exactly the lightest arm; the tests compare it against
  every combination of a reduced option set.

Estimates, marked in the config files: the transmission masses, tensions and diameters,
and any motor field listed in that motor's `estimated` (none in `motors.toml`).
