"""Drive choice: one pass from the wrist (J7) in to the shoulder (J1).

A joint's load comes only from what lies beyond it, and a drive loads only the joints
before it. So taking the lightest drive that passes at each joint, working inwards,
gives the lightest arm; tests/ checks this against every combination.
"""
import math
from dataclasses import dataclass

from .arm import Arm, Body, build_arm
from .drives import Drive
from .loads import JointLoad, joint_load


@dataclass
class Check:
    drive: Drive
    load: JointLoad
    rated_use: float            # holding torque / rated torque at the joint
    peak_use: float             # (holding + accel) torque / peak torque at the joint
    speed: float                # rad/s the joint reaches while holding its load
    speed_req: float
    diameter: float             # mm, output pulley or drum
    diameter_max: float
    use: dict[str, float]       # each check as demand / allowed; above 1 fails

    @property
    def worst(self) -> float:
        return max(self.use.values())

    @property
    def ok(self) -> bool:
        return self.worst <= 1

    @property
    def fails(self) -> list[str]:
        return [name for name, v in self.use.items() if v > 1]


@dataclass
class Selection:
    arm: Arm
    joints: list[Check]         # J1..J7
    drive_bodies: list[Body]

    @property
    def feasible(self) -> bool:
        return all(c.ok for c in self.joints)

    @property
    def drive_mass(self) -> float:
        """Motors with their overhead and transmissions, kg."""
        return sum(b.mass for b in self.drive_bodies)

    @property
    def arm_mass(self) -> float:
        return self.arm.structure_mass + self.drive_mass


def drive_body(drive: Drive, j: int, arm: Arm) -> Body:
    return Body(drive.name, drive.mass_kg, arm.motor_x[j], 0.0, j - 1)


def check(arm: Arm, j: int, bodies: list[Body], drive: Drive, cfg: dict) -> Check:
    m, spec = cfg["motors"], cfg["joint"][j]
    load = joint_load(arm, j, bodies, drive.reflected_inertia, cfg["payload"]["accel_m_s2"])
    rated_use, peak_use = load.torque_hold / drive.rated_Nm, load.torque_peak / drive.peak_Nm
    speed = drive.speed(load.torque_hold)
    diameter = drive.diameter_mm(load.torque_peak)
    diameter_max = spec["max_drum_mm"] * arm.height / cfg["structure"]["reference_height_m"]
    use = {"rated": rated_use / m["continuous_factor"],
           "peak": peak_use / m["peak_factor"],
           "speed": spec["speed_rad_s"] / speed if speed > 0 else math.inf,
           "size": diameter / diameter_max}
    return Check(drive, load, rated_use, peak_use, speed, spec["speed_rad_s"],
                 diameter, diameter_max, use)


def select_drives(arm: Arm, options: list[list[Drive]], cfg: dict) -> Selection:
    """Lightest passing drive per joint from that joint's options, J7 first. Where none
    passes, the one closest to passing."""
    checks: list[Check] = []
    bodies: list[Body] = []
    for j in reversed(range(len(arm.joint_x))):
        best = check(arm, j, arm.bodies + bodies, options[j][0], cfg)
        for drive in options[j][1:]:
            if best.ok:
                break
            c = check(arm, j, arm.bodies + bodies, drive, cfg)
            if c.ok or c.worst < best.worst:
                best = c
        checks.append(best)
        bodies.append(drive_body(best.drive, j, arm))
    return Selection(arm, checks[::-1], bodies)


def evaluate(arm: Arm, drives: list[Drive], cfg: dict) -> Selection:
    """Check a given drive per joint, J1..J7."""
    bodies = [drive_body(drive, j, arm) for j, drive in enumerate(drives)]
    return Selection(arm, [check(arm, j, arm.bodies + bodies, drive, cfg)
                           for j, drive in enumerate(drives)], bodies)


def max_payload(height: float, options: list[list[Drive]], cfg: dict,
                hi: float = 30.0, tol: float = 0.01) -> float:
    """Heaviest payload some drive choice can carry at this height, kg."""
    def feasible(kg: float) -> bool:
        return select_drives(build_arm(height, cfg, kg), options, cfg).feasible

    if not feasible(0.0):
        return 0.0
    lo = 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if feasible(mid) else (lo, mid)
    return lo
