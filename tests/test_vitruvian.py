import copy
import itertools
import math
import tomllib
from dataclasses import replace
from pathlib import Path

import pytest

from run import override
from vitruvian.arm import Arm, Body, build_arm
from vitruvian.drives import drive_options
from vitruvian.loads import G, joint_load
from vitruvian.motors import load_motors
from vitruvian.selection import evaluate, max_payload, select_drives

ROOT = Path(__file__).parents[1]
CFG = tomllib.loads((ROOT / "config.toml").read_text())
CATALOG = load_motors(ROOT / "motors.toml")
OPTIONS = drive_options(CATALOG, CFG)
UNLIMITED = copy.deepcopy(CFG)
UNLIMITED["transmission"].pop("max_total_ratio", None)


def option(name: str):
    """Any drive by name, ignoring the total-ratio limit."""
    return next(d for joint in drive_options(CATALOG, UNLIMITED) for d in joint if d.name == name)


def test_single_link_closed_form():
    """Horizontal rod (m, L) with a point payload p at its tip, driven at its base."""
    m, L, p, a, rotor = 2.0, 0.5, 3.0, 4.0, 0.01
    arm = Arm(1.0, {}, [0.0], [0.0], [Body("rod", m, L / 2, m * L**2 / 12, 0)],
              Body("payload", p, L, 0.0, 0))
    load = joint_load(arm, 0, arm.bodies, rotor, a)
    assert load.torque_hold == pytest.approx(m * G * L / 2 + p * G * L)
    assert load.torque_accel == pytest.approx((m * L**2 / 3 + p * L**2 + rotor) * a / L)
    assert load.force_hold == pytest.approx((m + p) * G)


def test_lengths_scale_with_height():
    short, tall = build_arm(1.0, CFG, 1.0), build_arm(2.0, CFG, 1.0)
    for link, length in short.lengths.items():
        assert tall.lengths[link] == pytest.approx(2 * length)


def test_speed_line_through_datasheet_points():
    motor = next(m for m in CATALOG if m.name == "AK45-10")
    rpm = lambda w: w * 60 / (2 * math.pi)
    assert motor.supply_V == 24
    assert rpm(motor.speed_rad_s(0)) == pytest.approx(180)
    assert rpm(motor.speed_rad_s(2.5)) == pytest.approx(120)
    assert rpm(replace(motor, max_V=48).speed_rad_s(0)) == pytest.approx(360)


def test_local_catalog(tmp_path):
    local = tmp_path / "motors.local.toml"
    assert load_motors(ROOT / "motors.toml", local) == CATALOG       # missing: skipped
    local.write_text('[[motor]]\nname = "X"\nrated_Nm = 1\npeak_Nm = 3\nmass_kg = 0.2\n'
                     'ratio = 10\nrotor_inertia_gcm2 = 100\nrated_rpm = 100\n'
                     'no_load_rpm = 150\nrated_V = 24\n')
    motors = load_motors(ROOT / "motors.toml", local)
    assert [m.name for m in motors if m.local] == ["X"]
    assert not any(m.local for m in CATALOG)
    local.write_text(local.read_text().replace('"X"', '"AK45-10"'))
    with pytest.raises(ValueError):
        load_motors(ROOT / "motors.toml", local)


def test_drive_options():
    belt = option("AK45-10 belt 10:1")
    assert belt.stages == 2 and belt.efficiency == pytest.approx(0.96**2)
    assert belt.rated_Nm == pytest.approx(2.5 * 10 * 0.96**2)
    assert belt.speed(0) == pytest.approx(option("AK45-10").speed(0) / 10)
    assert not any(d.name == "AK45-10 capstan 10:1" for joint in OPTIONS for d in joint)
    assert option("AK45-10 capstan 4:1").diameter_mm(100) == pytest.approx(2000 * 100 / 1200)


def test_allow_overrides_exclude_per_joint():
    for spec, joint in zip(CFG["joint"], OPTIONS):
        has = any(d.motor.name == "AKH70-16" for d in joint)
        assert has == ("AKH70-16" in spec.get("allow", []))


def test_total_ratio_limit():
    cfg = copy.deepcopy(UNLIMITED)
    cfg["transmission"]["max_total_ratio"] = 50
    options = drive_options(CATALOG, cfg)
    assert all(d.total_ratio <= 50 for joint in options for d in joint)
    assert any(d.name == "AK45-10 capstan 5:1" for d in options[0])
    assert not any(d.name == "AK45-10 capstan 6:1" for d in options[0])
    assert any(d.name == "AK45-10 capstan 6:1" for d in drive_options(CATALOG, UNLIMITED)[0])


def test_direct_and_exclude_overrides():
    cfg = copy.deepcopy(CFG)
    override(cfg, CATALOG, direct=True, exclude=[])
    options = drive_options(CATALOG, cfg)
    assert all(d.kind == "direct" for joint in options for d in joint)
    assert all(len(joint) == len(CATALOG) for joint in options)
    cfg = copy.deepcopy(CFG)
    override(cfg, CATALOG, direct=False, exclude=["AKH70-16"])
    assert not any(d.motor.name == "AKH70-16" for joint in drive_options(CATALOG, cfg) for d in joint)
    with pytest.raises(SystemExit):
        override(copy.deepcopy(CFG), CATALOG, direct=False, exclude=["AKH70-61"])


def test_drive_never_loads_its_own_joint():
    arm = build_arm(1.8, CFG, 2.0)
    light, heavy = OPTIONS[6][0], OPTIONS[6][-1]
    a = evaluate(arm, [light] * 6 + [heavy], CFG)
    b = evaluate(arm, [light] * 7, CFG)
    assert a.joints[6].load.torque_hold == pytest.approx(b.joints[6].load.torque_hold)
    assert a.joints[0].load.torque_hold > b.joints[0].load.torque_hold


@pytest.mark.parametrize("height,payload", [(1.0, 1.0), (1.4, 2.0), (1.6, 4.0), (1.8, 3.0),
                                            (1.8, 4.0)])
def test_greedy_matches_brute_force(height, payload):
    subset = [option(n) for n in ("AK40-10", "AK45-10 capstan 2:1", "AK60-39",
                                  "AKH70-16 belt 3:1")]
    arm = build_arm(height, CFG, payload)
    greedy = select_drives(arm, [sorted(subset, key=lambda d: d.mass_kg)] * 7, CFG)
    feasible = [s for combo in itertools.product(subset, repeat=len(arm.joint_x))
                if (s := evaluate(arm, list(combo), CFG)).feasible]
    assert greedy.feasible == bool(feasible)
    if feasible:
        assert greedy.drive_mass == pytest.approx(min(s.drive_mass for s in feasible))


def test_max_payload_is_the_feasibility_edge():
    kg = max_payload(1.5, OPTIONS, CFG)
    assert select_drives(build_arm(1.5, CFG, kg), OPTIONS, CFG).feasible
    assert not select_drives(build_arm(1.5, CFG, kg + 0.05), OPTIONS, CFG).feasible
