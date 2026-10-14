"""Load motor/gearbox catalog from data/motors."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Motor:
    name: str
    peak_torque_Nm: float
    continuous_torque_Nm: float
    max_speed_rpm: float
    mass_kg: float
    rotor_inertia_kgm2: float
    cost_eur: float
    source: str = ""


@dataclass
class Gearbox:
    name: str
    ratio: float
    efficiency: float
    peak_torque_Nm: float
    max_input_speed_rpm: float
    mass_kg: float
    cost_eur: float
    source: str = ""


def load_motors(path: str | Path) -> list[Motor]:
    with open(path) as f:
        return [Motor(**d) for d in yaml.safe_load(f)]


def load_gearboxes(path: str | Path) -> list[Gearbox]:
    with open(path) as f:
        return [Gearbox(**d) for d in yaml.safe_load(f)]
