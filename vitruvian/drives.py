"""Drives: a motor module, direct or through a belt or capstan stage after its gearbox."""
import math
from dataclasses import dataclass

from .motors import Motor


@dataclass
class Drive:
    motor: Motor
    kind: str                   # "direct", or a [[drive]] name from the config
    ratio: float                # reduction after the module's gearbox
    stages: int
    efficiency: float
    mass_kg: float              # motor with overhead, plus the transmission
    min_diameter_mm: float      # output pulley or drum set by the stage ratio alone
    tension_N: float            # allowed working tension in the last stage

    @property
    def name(self) -> str:
        return self.motor.name if self.kind == "direct" else f"{self.motor.name} {self.kind} {self.ratio:g}:1"

    @property
    def short(self) -> str:
        motor = self.motor.name.removeprefix("AKH").removeprefix("AK")
        return motor if self.kind == "direct" else f"{motor} {self.kind[0].upper()}{self.ratio:g}"

    @property
    def total_ratio(self) -> float:
        """Module gearbox × extra stage: what backdriving the joint has to turn through."""
        return self.motor.ratio * self.ratio

    @property
    def rated_Nm(self) -> float:
        return self.motor.rated_Nm * self.ratio * self.efficiency

    @property
    def peak_Nm(self) -> float:
        return self.motor.peak_Nm * self.ratio * self.efficiency

    @property
    def reflected_inertia(self) -> float:
        """Rotor inertia as the joint sees it, kg m²."""
        return self.motor.rotor_inertia_gcm2 * 1e-7 * (self.motor.ratio * self.ratio) ** 2

    def speed(self, joint_torque_Nm: float) -> float:
        """Joint speed, rad/s, while delivering joint_torque_Nm."""
        module_torque = joint_torque_Nm / (self.ratio * self.efficiency)
        return self.motor.speed_rad_s(module_torque) / self.ratio

    def diameter_mm(self, joint_torque_Nm: float) -> float:
        """Output pulley or drum carrying joint_torque_Nm; 0 when direct."""
        if self.kind == "direct":
            return 0.0
        return max(self.min_diameter_mm, 2000 * joint_torque_Nm / self.tension_N)


def drive_options(catalog: list[Motor], cfg: dict) -> list[list[Drive]]:
    """Per joint, lightest first: each allowed motor direct and through each drive type and
    ratio, within the total-ratio limit."""
    m, t = cfg["motors"], cfg["transmission"]
    limit = t.get("max_total_ratio", math.inf)
    drives = []
    for motor in catalog:
        base = motor.mass_kg * (1 + m["overhead"])
        drives.append(Drive(motor, "direct", 1.0, 0, 1.0, base, 0.0, math.inf))
        for d in cfg["drive"]:
            for ratio in t["ratios"]:
                stages = math.ceil(math.log(ratio) / math.log(d["max_stage_ratio"]) - 1e-9)
                if stages > d["max_stages"]:
                    continue
                stage = ratio ** (1 / stages)
                drives.append(Drive(
                    motor, d["name"], ratio, stages, d["efficiency"] ** stages,
                    base + stages * (d["stage_kg"] + d["kg_per_ratio"] * stage),
                    stage * d["input_diameter_mm"], d["tension_N"]))
    drives = sorted((d for d in drives if d.total_ratio <= limit), key=lambda d: (d.mass_kg, d.ratio))
    return [[d for d in drives
             if d.motor.name not in m["exclude"] or d.motor.name in spec.get("allow", [])]
            for spec in cfg["joint"]]
