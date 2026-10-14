"""Motor + gearbox -> joint-side torque, speed, mass, inertia."""
from dataclasses import dataclass

from .catalog import Gearbox, Motor


@dataclass
class Actuator:
    motor: Motor
    gearbox: Gearbox

    @property
    def peak_torque_Nm(self) -> float:
        raise NotImplementedError

    @property
    def continuous_torque_Nm(self) -> float:
        raise NotImplementedError

    @property
    def max_speed_rad_s(self) -> float:
        raise NotImplementedError

    @property
    def mass_kg(self) -> float:
        raise NotImplementedError

    @property
    def reflected_inertia_kgm2(self) -> float:
        raise NotImplementedError
