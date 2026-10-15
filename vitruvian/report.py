"""Terminal tables."""
from itertools import groupby

from .motors import Motor
from .selection import Selection

JOINT_HEADER = (
    f"  {'joint':<18} {'drive':<26} {'x m':>6} {'out kg':>6} {'I kgm²':>7} {'α r/s²':>6} "
    f"{'F hold':>6} {'F peak':>6} {'τ hold':>6} {'τ acc':>6} {'τ peak':>6} {'rated':>6} "
    f"{'peak':>6} {'ω':>5} {'ω req':>5} {'Ø':>5} {'Ø max':>5}\n"
    f"  {'':<18} {'':<26} {'':>6} {'':>6} {'':>7} {'':>6} {'N':>6} {'N':>6} {'Nm':>6} "
    f"{'Nm':>6} {'Nm':>6} {'used':>6} {'used':>6} {'r/s':>5} {'r/s':>5} {'mm':>5} {'mm':>5}")


def preamble(catalog: list[Motor], cfg: dict) -> str:
    p, m = cfg["payload"], cfg["motors"]
    lines = [f"payload accel {p['accel_m_s2']:g} m/s²   limits: hold <= {m['continuous_factor']:.0%} "
             f"rated, hold + accel <= {m['peak_factor']:.0%} peak   "
             f"motor overhead +{m['overhead']:.0%}",
             "motors (* = estimated mass, x = excluded except where allowed, "
             "local = from the local catalog):"]
    for motor in catalog:
        star = "*" if "mass_kg" in motor.estimated else " "
        excluded = "x" if motor.name in m["exclude"] else " "
        allowed = [j["name"] for j in cfg["joint"] if motor.name in j.get("allow", [])]
        lines.append(f"  {excluded} {motor.name:<11} {motor.mass_kg * 1000:4.0f} g{star}  "
                     f"{motor.rated_Nm:5.1f} / {motor.peak_Nm:4.1f} Nm   "
                     f"{motor.speed_rad_s(0):5.1f} rad/s no-load at {motor.supply_V:g} V" +
                     (f"   allowed at {' '.join(allowed)}" if allowed else "") +
                     ("   local" if motor.local else ""))
    limit = cfg["transmission"].get("max_total_ratio")
    lines.append("drives: " + ", ".join(["direct"] + [
        f"{d['name']} (≤{d['max_stage_ratio']}:1 × {d['max_stages']}, η {d['efficiency']:.0%}/stage)"
        for d in cfg["drive"]]) +
        (f"   total ratio <= {limit:g}:1 for backdrivability" if limit else ""))
    return "\n".join(lines)


def detail(sel: Selection, cfg: dict) -> str:
    a, L = sel.arm, sel.arm.lengths
    lines = [f"\n{a.height:.2f} m, payload {a.payload.mass:g} kg   upper arm {L['upper_arm']:.3f}  "
             f"forearm {L['forearm']:.3f}  hand {L['hand']:.3f} m   structure "
             f"{a.structure_mass:.2f} + drives {sel.drive_mass:.2f} = {sel.arm_mass:.2f} kg   "
             f"{'OK' if sel.feasible else 'INFEASIBLE'}",
             JOINT_HEADER]
    for spec, xj, c in zip(cfg["joint"], a.joint_x, sel.joints):
        l = c.load
        lines.append(
            f"  {spec['name'] + ' ' + spec['label']:<18} {c.drive.name:<26} {xj:6.3f} "
            f"{l.mass_out:6.2f} {l.inertia:7.4f} {l.alpha:6.1f} {l.force_hold:6.1f} "
            f"{l.force_peak:6.1f} {l.torque_hold:6.2f} {l.torque_accel:6.2f} {l.torque_peak:6.2f} "
            f"{c.rated_use:6.0%} {c.peak_use:6.0%} {c.speed:5.1f} {c.speed_req:5.1f} "
            f"{c.diameter:5.0f} {c.diameter_max:5.0f}"
            f"{'' if c.ok else '  ✗ ' + ' '.join(c.fails)}")
    return "\n".join(lines)


def span(values: list[float], fmt: str) -> str:
    lo, hi = format(values[0], fmt), format(values[-1], fmt)
    return lo if lo == hi else f"{lo}–{hi}"


def failing(sel: Selection, cfg: dict) -> str:
    return "; ".join(f"{spec['name']} {' '.join(c.fails)}"
                     for spec, c in zip(cfg["joint"], sel.joints) if not c.ok)


def summary(payload: float, sels: list[Selection], cfg: dict) -> str:
    """One line per run of heights that share the same drives."""
    names = [j["name"] for j in cfg["joint"]]
    lines = [f"\npayload {payload:g} kg   (B = belt, C = capstan, number = extra ratio)",
             f"  {'height m':<10} " + " ".join(f"{n:<12}" for n in names) +
             f" {'drives kg':>9} {'arm kg':>10}  status"]
    key = lambda s: (tuple(c.drive.short for c in s.joints), s.feasible)
    for (drives, feasible), group in groupby(sels, key=key):
        group = list(group)
        lines.append(f"  {span([s.arm.height for s in group], '.2f'):<10} " +
                     " ".join(f"{d:<12}" for d in drives) +
                     f" {group[0].drive_mass:9.2f} {span([s.arm_mass for s in group], '.2f'):>10}  " +
                     ("OK" if feasible else "fails " + failing(group[0], cfg)))
    return "\n".join(lines)


def overview(heights: list[float], limits: list[float], cfg: dict) -> str:
    every = round(cfg["sweep"]["overview_every_m"] * 1000)
    shown = [(h, kg) for h, kg in zip(heights, limits) if round(h * 1000) % every == 0]
    return ("\nmax payload, kg (heaviest any drive choice carries)\n"
            "  height m " + " ".join(f"{h:5.1f}" for h, _ in shown) + "\n"
            "  payload  " + " ".join(f"{kg:5.1f}" for _, kg in shown))
